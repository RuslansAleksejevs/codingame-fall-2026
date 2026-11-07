// Original referee observations for checking the external-teacher bridge.
import com.codingame.game.Player;
import com.google.gson.*;
import engine.Board;
import engine.task.TaskManager;
import java.io.*;
import java.util.*;

public class InputOracle {
    public static void main(String[] args) throws Exception {
        BufferedReader input=new BufferedReader(new InputStreamReader(System.in));Gson gson=new Gson();String line;
        while((line=input.readLine())!=null){
            JsonObject job=new JsonParser().parse(line).getAsJsonObject();
            Player.registerPlayer(new Player(0));Player.registerPlayer(new Player(1));
            Properties properties=new Properties();for(String key:new String[]{"nodes","units","edges"})properties.put(key,Oracle.join(job.getAsJsonArray(key)));
            Board board=new Board(properties,new Random(0),null,null,null,null,null,null);Oracle.settle(board);
            List<String[]> observations=new ArrayList<>();int turn=0;
            observations.add(new String[]{board.getInput(true,Player.getPlayer(0),true),board.getInput(true,Player.getPlayer(1),true)});
            for(JsonElement row:job.getAsJsonArray("actions")){
                JsonArray actions=row.getAsJsonArray();TaskManager manager=new TaskManager();
                for(int p=0;p<2;p++)manager.parseTasks(Player.getPlayer(p),board,actions.get(p).getAsString(),3);
                if(manager.hasDebug())manager.popTasks();do{board.applyActions(manager,null);}while(manager.hasTasks());
                turn++;if(turn<200){Oracle.settle(board);Oracle.terminal(board);}
                observations.add(new String[]{board.getInput(false,Player.getPlayer(0),true),board.getInput(false,Player.getPlayer(1),true)});
            }
            System.out.println(gson.toJson(observations));
        }
    }
}
