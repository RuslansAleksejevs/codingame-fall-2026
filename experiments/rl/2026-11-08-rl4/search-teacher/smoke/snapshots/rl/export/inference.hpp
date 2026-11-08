// Deployment inference: vectorize independent output neurons, preserving sum order.
#pragma once
#include "../models/policy.hpp"

namespace rl {
struct FastNetwork {
    const Network& original;
    const int maximum_action_kind;
    std::vector<std::vector<float>> transposed;
    explicit FastNetwork(const Network& net,int maximum_kind=6):original(net),maximum_action_kind(maximum_kind) {
        for (size_t layer=0; layer<net.weights.size(); ++layer) {
            int inputs=net.dims[layer], outputs=net.dims[layer+1];
            if(inputs>256 || outputs>256) throw std::runtime_error("Unsupported layer size");
            transposed.emplace_back(inputs*outputs);
            for(int k=0;k<inputs;++k) for(int j=0;j<outputs;++j)
                transposed.back()[k*outputs+j]=net.weights[layer][j*inputs+k];
        }
    }
    float evaluate(const std::array<float,FEATURES>& x) const {
        alignas(64) float a[256], b[256];
        std::copy(x.begin(),x.end(),a);
        for(size_t layer=0;layer<transposed.size();++layer) {
            int inputs=original.dims[layer], outputs=original.dims[layer+1];
            std::copy(original.bias[layer].begin(),original.bias[layer].end(),b);
            for(int k=0;k<inputs;++k) {
                const float* w=transposed[layer].data()+k*outputs;
                const float value=a[k];
                for(int j=0;j<outputs;++j) b[j]+=w[j]*value;
            }
            for(int j=0;j<outputs;++j)
                a[j]=layer+1==transposed.size()?b[j]:std::max(0.f,b[j]);
        }
        return a[0];
    }
    std::string act(const State& s,int p,int style=2) const {
        Decoder decoder(s,p,style);
        return decoder.run([&](const std::vector<Candidate>& candidates,const Decoder& dec) {
            int best=0;float value=-1e30;
            for(int j=0;j<int(candidates.size());++j) {
                if(candidates[j].kind>maximum_action_kind) continue;
                float candidate=evaluate(dec.features(candidates[j]));
                if(candidate>value){best=j;value=candidate;}
            }
            return best;
        });
    }
};
}
