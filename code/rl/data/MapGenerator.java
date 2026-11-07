// Expose the pinned referee's original map generator without rendering.
import com.codingame.game.Player;
import com.google.gson.Gson;
import engine.Board;
import java.io.*;
import java.util.*;

public class MapGenerator {
    public static void main(String[] args) throws Exception {
        BufferedReader input = new BufferedReader(new InputStreamReader(System.in));
        Gson gson = new Gson();
        String line;
        while ((line = input.readLine()) != null) {
            long seed = Long.parseLong(line.trim());
            Player.registerPlayer(new Player(0)); Player.registerPlayer(new Player(1));
            Properties properties = new Properties();
            try {
                new Board(properties, new Random(seed), null, null, null, null, null, null);
            } catch (NullPointerException e) {
                // Board stores all generated parameters before constructing BoardView.
                // Only this expected renderer failure is accepted; game generation is unmodified.
                if (e.getStackTrace().length == 0 || !e.getStackTrace()[0].getClassName().equals("view.BoardView")) throw e;
            }
            Map<String,String> result = new TreeMap<>();
            for (String key : new String[]{"nodes", "units", "edges"}) {
                if (!properties.containsKey(key)) throw new IllegalStateException("Incomplete map: " + key);
                result.put(key, properties.getProperty(key));
            }
            System.out.println(gson.toJson(result));
        }
    }
}
