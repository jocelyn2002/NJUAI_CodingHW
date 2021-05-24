package controllers.limitdepthfirst;

import core.game.Observation;
import core.game.StateObservation;
import core.player.AbstractPlayer;
import ontology.Types;
import tools.ElapsedCpuTimer;
import tools.Vector2d;

import java.util.ArrayList;

public class Agent extends AbstractPlayer{
    private double big_number = 100000;
    private int max_depth=2;

    private static ArrayList<StateObservation> real_states;
    private static ArrayList<StateObservation> virtual_states;

    /**
     * initialize all variables for the agent
     * @param stateObs Observation of the current state.
     * @param elapsedTimer Timer when the action returned is due.
     */
    public Agent(StateObservation stateObs, ElapsedCpuTimer elapsedTimer){
        real_states = new ArrayList<>();
        virtual_states = new ArrayList<>();
    }

    @Override
    public Types.ACTIONS act(StateObservation stateObs, ElapsedCpuTimer elapsedTimer) {
        real_states.add(stateObs.copy());

        ArrayList<Types.ACTIONS> real_actions = stateObs.getAvailableActions();
        Types.ACTIONS chosen_action=null;
        double max_value=-0;
        for (Types.ACTIONS action: real_actions){
            StateObservation stcopy = stateObs.copy();
            stcopy.advance(action);
            double new_value = evaluate(stcopy, 1);
            if (max_value < new_value){
                max_value=new_value;
                chosen_action=action;
            }
        }
        return chosen_action;
    }

    private double eval(StateObservation stateObs){
        Vector2d ap = new Vector2d(stateObs.getAvatarPosition());//玩家位置
        Vector2d dp = new Vector2d(stateObs.getImmovablePositions()[1].get(0).position);

        double total_distance;
        try {
            Vector2d kp = new Vector2d(stateObs.getMovablePositions()[0].get(0).position);
            total_distance=ap.dist(kp)+kp.dist(dp);
        }
        catch(RuntimeException e) {
            total_distance=ap.dist(dp);
        }
        return big_number - total_distance;
    }
    private double evaluate(StateObservation stateObs, int depth) {
        // 判断是否赢了
        if (stateObs.getGameWinner() == Types.WINNER.PLAYER_WINS)
            return 2 * big_number;
        // 判断是否重复
        for (StateObservation ob : real_states)
            if (ob.equalPosition(stateObs))
                return 0;
        for (StateObservation ob : virtual_states)
            if (ob.equalPosition(stateObs))
                return 0;
        // 判断是否死了
        if (stateObs.isGameOver())
            return 0;
        // 底层节点
        if (depth == max_depth)
            return eval(stateObs);

        // 非底层节点
        virtual_states.add(stateObs);
        double max_value=0;
        ArrayList<Types.ACTIONS> actions = stateObs.getAvailableActions();
        for (Types.ACTIONS action : actions) {
            StateObservation stcopy = stateObs.copy();
            stcopy.advance(action);
            double new_value = evaluate(stcopy, depth+1);
            if (max_value < new_value)
                    max_value = new_value;
        }
//        System.out.println(max_value);
        virtual_states.remove(virtual_states.size()-1);
        return max_value;
    }
}