package controllers.depthfirst;

import controllers.Astar.STO;
import core.game.Observation;
import core.game.StateObservation;
import core.player.AbstractPlayer;
import ontology.Types;
import tools.ElapsedCpuTimer;
import tools.Vector2d;

import java.util.ArrayList;



public class Agent extends AbstractPlayer{
    protected int block_size;

    protected static ArrayList<Types.ACTIONS> method;
    private static ArrayList<StateObservation> current_states;
    private static boolean found_path;
    private static boolean first_run;
    /**
     * initialize all variables for the agent
     * @param stateObs Observation of the current state.
     * @param elapsedTimer Timer when the action returned is due.
     */
    public Agent(StateObservation stateObs, ElapsedCpuTimer elapsedTimer){
        block_size = stateObs.getBlockSize();

        method = new ArrayList<>();
        current_states = new ArrayList<>();
        first_run=true;
        found_path=false;
    }

    /**
     * return ACTION_NIL on every call to simulate doNothing player
     * @param stateObs Observation of the current state.
     * @param elapsedTimer Timer when the action returned is due.
     * @return 	ACTION_NIL all the time
     */
    @Override
    public Types.ACTIONS act(StateObservation stateObs, ElapsedCpuTimer elapsedTimer) {
        //当已经找到路径
        if (found_path)
        {
            Types.ACTIONS this_action = method.get(0);
            method.remove(0);
//            System.out.println(method);
            return this_action;
        }
        else {
            search(stateObs);
            return null;
        }
    }

    private void search(StateObservation stateObs){
        //还在寻找
        if (first_run)
        {
            current_states.add(stateObs);
            first_run=false;
        }

        ArrayList<Types.ACTIONS> actions = stateObs.getAvailableActions();

        for (Types.ACTIONS action : actions) {
            StateObservation stCopy = stateObs.copy();
            stCopy.advance(action);
            //判断是否赢了
            if (stCopy.getGameWinner()== Types.WINNER.PLAYER_WINS) {
                System.out.println("yeah!!!!!!");
                found_path=true;
                method.add(action);
            }
            //判断是否死了
            if (stCopy.isGameOver()) continue;
            //判断是否为重复状态
            boolean repeated=false;
            for (StateObservation ob:current_states)
                if (stCopy.equalPosition(ob)) {
                    repeated=true;
                    break;
                }
            if (repeated) {
                continue;
            }
            if (!found_path) {
                //若通过上述两步，则为一个新的状态，添加状态和动作列表
                current_states.add(stCopy.copy());
                method.add(action);
//                System.out.println(method);
                //此时胜利,则置found_path为真
                search(stCopy.copy());
            }
        }
        //如果执行到这里说明此路不通,删除列表中的自己
        if (!found_path){
            method.remove(method.size()-1);
//            System.out.println(method);
        }
    }

}