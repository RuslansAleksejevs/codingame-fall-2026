// Differential oracle using the unmodified pinned Java rules, without a renderer.
import com.codingame.game.Player;
import com.google.gson.*;
import engine.Board;
import engine.Node;
import engine.Triangle;
import engine.task.TaskManager;
import java.io.*;
import java.util.*;

public class Oracle {
    static Gson gson = new Gson();
    static void settle(Board b) { while (b.finalizeTurn(null)); }
    static Map<String,Object> state(Board b, int turn, boolean done) {
        Map<String,Object> s = new LinkedHashMap<>();
        s.put("turn",turn);s.put("score",new int[]{Player.getPlayer(0).getScore(),Player.getPlayer(1).getScore()});
        List<int[]> units=new ArrayList<>(),edges=new ArrayList<>(),triangles=new ArrayList<>();
        for(Node n:b.nodes){units.add(n.units.clone());for(Node m:n.neighbors)if(n.getId()<m.getId())edges.add(new int[]{n.getId(),m.getId()});}
        for(Triangle t:b.triangles)triangles.add(new int[]{t.getNode1().getId(),t.getNode2().getId(),t.getNode3().getId(),t.getOwner()==null?-1:t.getOwner().getIndex(),t.canCapture(Player.getPlayer(0))?1:0,t.canCapture(Player.getPlayer(1))?1:0});
        s.put("units",units);s.put("edges",edges);s.put("triangles",triangles);s.put("done",done);return s;
    }
    static boolean terminal(Board b) {
        int[] army=new int[2],income=new int[2];for(Node n:b.nodes)for(int p=0;p<2;p++)army[p]+=n.units[p];
        for(Triangle t:b.triangles)if(t.getOwner()!=null)income[t.getOwner().getIndex()]++;
        boolean done=false;
        for(int p=0;p<2;p++)if((army[p]==0&&income[p]==0)||(army[p]==1&&income[p]==0&&Player.getPlayer(p).getScore()<Player.getPlayer(1-p).getScore())||income[1-p]>=b.triangles.size()*0.8){Player.getPlayer(p).setScore(-1);done=true;}
        return done;
    }
    static String join(JsonArray data) {List<String> values=new ArrayList<>();for(JsonElement row:data){List<String> v=new ArrayList<>();for(JsonElement item:row.getAsJsonArray())v.add(item.getAsString());values.add(String.join(",",v));}return String.join("_",values);}
    public static void main(String[] args)throws Exception {
        BufferedReader r=new BufferedReader(new InputStreamReader(System.in));String line;
        while((line=r.readLine())!=null){
            JsonObject job=new JsonParser().parse(line).getAsJsonObject();
            Player.registerPlayer(new Player(0));Player.registerPlayer(new Player(1));
            Properties p=new Properties();for(String key:new String[]{"nodes","units","edges"})p.put(key,join(job.getAsJsonArray(key)));
            Board b=new Board(p,new Random(0),null,null,null,null,null,null);settle(b);
            List<Map<String,Object>> states=new ArrayList<>();states.add(state(b,0,false));
            int turn=0;for(JsonElement item:job.getAsJsonArray("actions")){
                TaskManager tm=new TaskManager();JsonArray a=item.getAsJsonArray();
                for(int i=0;i<2;i++)tm.parseTasks(Player.getPlayer(i),b,a.get(i).getAsString(),3);
                // Debug commands have no mechanical effect; remove them without rendering.
                if(tm.hasDebug())tm.popTasks();
                do{b.applyActions(tm,null);}while(tm.hasTasks());
                turn++;boolean done=turn>=200;
                if(!done){settle(b);done=terminal(b);}
                states.add(state(b,turn,done));
            }
            System.out.println(gson.toJson(states));
        }
    }
}
