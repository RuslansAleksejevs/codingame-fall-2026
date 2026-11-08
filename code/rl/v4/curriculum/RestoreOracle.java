// Direct boundary restoration using unmodified pinned Java mechanics.
import com.codingame.game.Player;
import com.google.gson.*;
import engine.Board;
import engine.Node;
import engine.Triangle;
import engine.task.TaskManager;
import java.io.*;
import java.lang.reflect.Field;
import java.util.*;

public class RestoreOracle {
    static Field field(Class<?> type,String name)throws Exception {Field f=type.getDeclaredField(name);f.setAccessible(true);return f;}
    static int owner(Object value){return value==null?-1:((Player)value).getIndex();}
    static Map<String,Object> full(Board board,int turn,boolean done)throws Exception {
        Map<String,Object> result=Oracle.state(board,turn,done);
        List<int[]> nodes=new ArrayList<>(),remaining=new ArrayList<>();List<Integer> initial=new ArrayList<>();
        for(Node n:board.nodes){nodes.add(new int[]{n.getX(),n.getY()});remaining.add(n.remainingUnits.clone());}
        for(Triangle t:board.triangles)initial.add(owner(field(Triangle.class,"initialOwner").get(t)));
        result.put("nodes",nodes);result.put("remaining",remaining);result.put("initial_owners",initial);
        result.put("surrounded",field(Board.class,"killedSurrounded").get(board));result.put("schema",1);
        result.put("phase","settled_predecision");result.put("queue",new ArrayList<>());return result;
    }
    static Board board(JsonObject source)throws Exception {
        Player.registerPlayer(new Player(0));Player.registerPlayer(new Player(1));
        Properties p=new Properties();for(String key:new String[]{"nodes","units","edges"})p.put(key,Oracle.join(source.getAsJsonArray(key)));
        Board b=new Board(p,new Random(0),null,null,null,null,null,null);Oracle.settle(b);return b;
    }
    static Board restore(JsonObject s)throws Exception {
        if(!s.get("phase").getAsString().equals("settled_predecision")||s.getAsJsonArray("queue").size()!=0)throw new IllegalArgumentException("Nonempty queue");
        Board b=board(s);JsonArray units=s.getAsJsonArray("units"),remaining=s.getAsJsonArray("remaining");
        for(int i=0;i<b.nodes.size();i++)for(int p=0;p<2;p++){
            b.nodes.get(i).units[p]=units.get(i).getAsJsonArray().get(p).getAsInt();
            b.nodes.get(i).remainingUnits[p]=remaining.get(i).getAsJsonArray().get(p).getAsInt();
        }
        JsonArray ts=s.getAsJsonArray("triangles"),initial=s.getAsJsonArray("initial_owners");
        if(ts.size()!=b.triangles.size())throw new IllegalArgumentException("Triangle count");
        for(int i=0;i<ts.size();i++){
            Triangle t=b.triangles.get(i);JsonArray row=ts.get(i).getAsJsonArray();
            if(t.getNode1().getId()!=row.get(0).getAsInt()||t.getNode2().getId()!=row.get(1).getAsInt()||t.getNode3().getId()!=row.get(2).getAsInt())throw new IllegalArgumentException("Triangle order");
            int own=row.get(3).getAsInt(),ini=initial.get(i).getAsInt();
            field(Triangle.class,"owner").set(t,own<0?null:Player.getPlayer(own));
            field(Triangle.class,"initialOwner").set(t,ini<0?null:Player.getPlayer(ini));
            field(Triangle.class,"canCapture").set(t,new boolean[]{row.get(4).getAsInt()!=0,row.get(5).getAsInt()!=0});
        }
        for(int p=0;p<2;p++)Player.getPlayer(p).setScore(s.getAsJsonArray("score").get(p).getAsInt());
        field(Board.class,"killedSurrounded").set(b,s.get("surrounded").getAsBoolean());
        field(Board.class,"gameTurn").set(b,s.get("turn").getAsInt());
        return b; // Do not settle again after restoring.
    }
    public static void main(String[] args)throws Exception {
        BufferedReader input=new BufferedReader(new InputStreamReader(System.in));String line;Gson gson=new Gson();
        while((line=input.readLine())!=null){JsonObject job=new JsonParser().parse(line).getAsJsonObject();
            boolean restored=job.has("snapshot");JsonObject source=restored?job.getAsJsonObject("snapshot"):job;
            Board b=restored?restore(source):board(source);int turn=restored?source.get("turn").getAsInt():0;
            boolean done=false;List<Map<String,Object>> states=new ArrayList<>();states.add(full(b,turn,done));
            for(JsonElement item:job.getAsJsonArray("actions")){
                if(done)throw new IllegalStateException("Action after terminal");
                TaskManager manager=new TaskManager();JsonArray actions=item.getAsJsonArray();
                for(int p=0;p<2;p++)manager.parseTasks(Player.getPlayer(p),b,actions.get(p).getAsString(),3);
                if(manager.hasDebug())manager.popTasks();do{b.applyActions(manager,null);}while(manager.hasTasks());
                turn++;done=turn>=200;if(!done){Oracle.settle(b);done=Oracle.terminal(b);}states.add(full(b,turn,done));
            }
            System.out.println(gson.toJson(states));
        }
    }
}