// Bounded simultaneous complete-plan search, isolated from PPO-v3 training.
#pragma once
#include "../league/rollout_league.cpp"
#include "../export/inference.hpp"
#include <iomanip>

namespace searchpilot {
using Clock = std::chrono::steady_clock;

rl::State clone(const rl::State& source) {
    rl::State result = source;
    for (size_t i = 0; i < result.ts.size(); ++i)
        result.ts[i] = std::make_shared<rl::Triangle>(*source.ts[i]);
    return result;
}

std::string sampled(const rl::FastNetwork& network, const rl::State& state,
                    int player, std::mt19937_64& rng, double temperature) {
    rl::Decoder decoder(state, player, 2);
    return decoder.run([&](const std::vector<rl::Candidate>& choices, const rl::Decoder& d) {
        std::vector<double> probabilities;
        double maximum = -1e30;
        for (const auto& choice : choices) {
            double logit = network.evaluate(d.features(choice)) / temperature;
            probabilities.push_back(logit);
            maximum = std::max(maximum, logit);
        }
        double sum = 0;
        for (auto& probability : probabilities) {
            probability = std::exp(probability - maximum);
            sum += probability;
        }
        double draw = std::generate_canonical<double, 53>(rng) * sum;
        for (int i = 0; i < int(probabilities.size()); ++i) {
            if (draw < probabilities[i]) return i;
            draw -= probabilities[i];
        }
        return int(probabilities.size()) - 1;
    });
}

unsigned long long state_seed(const rl::State& state, int player) {
    // Stable across processes/standard-library implementations; no address hash.
    unsigned long long hash = 1469598103934665603ULL;
    for (unsigned char byte : state.json()) { hash ^= byte; hash *= 1099511628211ULL; }
    return hash ^ (0x9e3779b97f4a7c15ULL * (player + 1));
}

struct Search {
    rl::Network actor, critic;
    std::array<rl::Network, 3> enemies;
    std::unique_ptr<rl::FastNetwork> policy, value;
    std::array<std::unique_ptr<rl::FastNetwork>, 3> responses;
    int depth, candidates;
    double budget_ms;
    std::string answer, info;

    Search(const char* actor_path, const char* critic_path, const char* enemy0,
           const char* enemy1, const char* enemy2, int horizon, int count, double budget)
        : depth(horizon), candidates(count), budget_ms(budget) {
        if (depth < 1 || depth > 2 || candidates < 1 || candidates > 4 || budget_ms < 0)
            throw std::runtime_error("Invalid bounded-search configuration");
        actor.load(actor_path); critic.load(critic_path);
        const char* paths[3] = {enemy0, enemy1, enemy2};
        for (int i = 0; i < 3; ++i) {
            enemies[i].load(paths[i]);
            responses[i] = std::make_unique<rl::FastNetwork>(enemies[i]);
        }
        policy = std::make_unique<rl::FastNetwork>(actor);
        value = std::make_unique<rl::FastNetwork>(critic);
    }

    double evaluate(const rl::State& state, int player) const {
        if (state.done)
            return state.score[player] > state.score[1-player] ? 1 : state.score[player] < state.score[1-player] ? -1 : 0;
        rl::Decoder own(state, player, 2), enemy(state, 1-player, 2);
        double a = value->evaluate(league::value_features(own));
        double b = value->evaluate(league::value_features(enemy));
        return std::clamp((a-b)/2., -1., 1.);
    }

    std::string act(const rl::State& root, int player) {
        auto began = Clock::now();
        auto elapsed = [&]() { return std::chrono::duration<double, std::milli>(Clock::now()-began).count(); };
        auto expired = [&]() { return budget_ms > 0 && elapsed() >= budget_ms; };
        std::string original = root.json();
        std::vector<std::string> plans{policy->act(root, player, 2)};
        if (candidates == 1) {
            auto micros=std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-began).count();
            answer=plans[0];
            info="{\"selected\":0,\"plans_generated\":1,\"complete_candidates\":0,\"transitions\":0,\"stopped_by_budget\":0,\"plan_us\":"+std::to_string(micros)+",\"depth\":0,\"values\":[]}";
            return answer;
        }
        int selected = 0, complete = 0, transitions = 0, stopped = 0;
        double best = -1e30, baseline = -1e30;
        std::vector<double> evaluated;
        std::array<std::string, 3> root_responses;
        // Every root opponent plan is selected from the same original state,
        // before inspecting or applying any candidate of the controlled player.
        for (int model = 0; model < 3; ++model) {
            if (expired()) { stopped = 1; break; }
            root_responses[model] = responses[model]->act(root, 1-player, 2);
        }
        std::mt19937_64 rng(state_seed(root, player));
        const double temperatures[3] = {.15, .35, .7};
        for (int candidate = 0; candidate < candidates && !stopped; ++candidate) {
            if (expired()) { stopped = 1; break; }
            if (candidate > 0) {
                auto plan = sampled(*policy, root, player, rng, temperatures[candidate-1]);
                if (std::find(plans.begin(), plans.end(), plan) != plans.end()) continue;
                plans.push_back(plan);
            }
            const int plan_index = int(plans.size())-1;
            std::array<double, 3> outcomes{};
            bool completed = true;
            for (int model = 0; model < 3; ++model) {
                if (expired()) { completed = false; break; }
                rl::State state = clone(root);
                std::string own = plans[plan_index], other = root_responses[model];
                int performed = 0;
                for (int turn = 0; turn < depth && !state.done; ++turn) {
                    if (turn > 0) {
                        if (expired()) { completed = false; break; }
                        // Both future actions are recomputed from the new state.
                        own = policy->act(state, player, 2);
                        other = responses[model]->act(state, 1-player, 2);
                    }
                    state.step(player == 0 ? own : other, player == 0 ? other : own);
                    ++performed; ++transitions;
                    if (state.parse_errors[0] != root.parse_errors[0] || state.parse_errors[1] != root.parse_errors[1])
                        throw std::runtime_error("Invalid simulated search plan");
                }
                if (!completed) break;
                outcomes[model] = std::pow(.995, performed - (state.done ? 1 : 0)) * evaluate(state, player);
            }
            if (!completed) { stopped = 1; break; }
            double mean = std::accumulate(outcomes.begin(), outcomes.end(), 0.)/3.;
            double combined = .5 * mean + .5 * *std::min_element(outcomes.begin(), outcomes.end());
            evaluated.push_back(combined); ++complete;
            // Keep the baseline unless an alternative clears a fixed margin.
            if (complete == 1) { baseline=best=combined; selected=0; }
            else if (combined > baseline + .02 && combined > best) { best=combined; selected=plan_index; }
        }
        if (root.json() != original) throw std::runtime_error("Search mutated its root state");
        auto micros = std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-began).count();
        std::ostringstream report;
        report << std::setprecision(9) << "{\"selected\":" << selected << ",\"plans_generated\":" << plans.size()
               << ",\"complete_candidates\":" << complete << ",\"transitions\":" << transitions
               << ",\"stopped_by_budget\":" << stopped << ",\"plan_us\":" << micros
               << ",\"depth\":" << depth << ",\"values\":[";
        for (size_t i = 0; i < evaluated.size(); ++i) { if (i) report << ','; report << evaluated[i]; }
        report << "]}"; info = report.str(); answer = plans[selected];
        return answer;
    }
};
static thread_local std::string last_error;
}

extern "C" {
void* search_new(const char* actor, const char* critic, const char* e0, const char* e1, const char* e2,
                 int depth, int candidates, double budget_ms) {
    try { return new searchpilot::Search(actor, critic, e0, e1, e2, depth, candidates, budget_ms); }
    catch (const std::exception& e) { searchpilot::last_error=e.what(); return nullptr; }
}
void search_delete(void* ptr) { delete static_cast<searchpilot::Search*>(ptr); }
const char* search_error() { return searchpilot::last_error.c_str(); }
const char* search_act(void* ptr, void* state, int player) {
    try { auto* s=static_cast<searchpilot::Search*>(ptr); s->act(*static_cast<rl::State*>(state), player); return s->answer.c_str(); }
    catch (const std::exception& e) { searchpilot::last_error=e.what(); return nullptr; }
}
const char* search_info(void* ptr) { return static_cast<searchpilot::Search*>(ptr)->info.c_str(); }
double search_value(void* ptr, void* state, int player) {
    return static_cast<searchpilot::Search*>(ptr)->evaluate(*static_cast<rl::State*>(state), player);
}
}