import com.codingame.gameengine.runner.MultiplayerGameRunner;
import com.codingame.gameengine.runner.simulate.GameResult;
import com.google.gson.Gson;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;

// Runs the unmodified author's referee; no server, account or leaderboard submission.
public class LocalMatch {
    public static void main(String[] args) throws Exception {
        if(args.length!=5) throw new IllegalArgumentException("seed league agent0 agent1 result.json");
        MultiplayerGameRunner runner=new MultiplayerGameRunner();
        runner.setSeed(Long.valueOf(args[0]));
        runner.setLeagueLevel(Integer.parseInt(args[1]));
        runner.addAgent(new String[]{args[2]}, "agent0");
        runner.addAgent(new String[]{args[3]}, "agent1");
        GameResult result=runner.simulate();
        Files.write(Paths.get(args[4]), new Gson().toJson(result).getBytes(StandardCharsets.UTF_8));
        System.out.println("RESULT "+result.scores+" failure="+result.failCause);
    }
}
