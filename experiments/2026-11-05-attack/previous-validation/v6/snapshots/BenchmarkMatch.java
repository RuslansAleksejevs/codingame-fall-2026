import com.codingame.gameengine.runner.MultiplayerGameRunner;
import com.codingame.gameengine.runner.simulate.GameResult;
import com.google.gson.Gson;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;

// Original, unmodified referee. Array commands support interpreters and paths with spaces.
public class BenchmarkMatch {
    static class Spec {
        long seed;
        int league;
        String[][] agents;
        String[] labels;
        String result;
    }
    public static void main(String[] args) throws Exception {
        Gson gson = new Gson();
        Spec spec = gson.fromJson(new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8), Spec.class);
        MultiplayerGameRunner runner = new MultiplayerGameRunner();
        runner.setSeed(spec.seed);
        runner.setLeagueLevel(spec.league);
        for (int i=0; i<2; i++) runner.addAgent(spec.agents[i], spec.labels[i]);
        GameResult result = runner.simulate();
        Files.write(Paths.get(spec.result), gson.toJson(result).getBytes(StandardCharsets.UTF_8));
        System.out.println("RESULT " + result.scores + " failure=" + result.failCause);
    }
}
