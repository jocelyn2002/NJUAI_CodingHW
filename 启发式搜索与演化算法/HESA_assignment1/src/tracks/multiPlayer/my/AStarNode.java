package tracks.multiPlayer.my;
import core.game.StateObservationMulti;
import ontology.Types;


public class AStarNode {
    public StateObservationMulti state; // 节点对应的状态
    public AStarNode father; // 父节点
    public Types.ACTIONS act; // 父节点如何操作转移到此
    public double f_value,g_value,h_value;


    /**
     * 创建节点
     *
      */

    public AStarNode(StateObservationMulti ob,AStarNode fnode,Types.ACTIONS a,double g,double h) {
        state = ob;
        update_father(fnode,a,g,h);
    }


    // 在找到更优路径时更新父节点
    public void update_father(AStarNode fnode,Types.ACTIONS a,double g,double h) {
        father = fnode;
        act = a;
        g_value = g;
        h_value = h;
        f_value = g+h;
    }
}
