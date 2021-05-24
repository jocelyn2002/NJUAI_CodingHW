package tracks.singlePlayer.advanced.myAdaptiveRHEA;

import core.game.StateObservation;
import ontology.Types;
import tracks.singlePlayer.tools.Heuristics.StateHeuristic;


public class myHeuristic extends StateHeuristic {

	private static final double HUGE_NEGATIVE = -1000.0;
	private static final double HUGE_POSITIVE =  1000.0;

	double initialNpcCounter = 0;

	public myHeuristic(StateObservation stateObs) {
	}

	public double evaluateState(StateObservation stateObs) {
		boolean gameOver = stateObs.isGameOver();
		Types.WINNER win = stateObs.getGameWinner();
		double rawScore = stateObs.getGameScore();

		if(gameOver && win == Types.WINNER.PLAYER_LOSES)
			return HUGE_NEGATIVE;

		if(gameOver && win == Types.WINNER.PLAYER_WINS)
			return HUGE_POSITIVE;

		// 使得avatar保持高血量
		int healthScore = stateObs.getAvatarHealthPoints();
//		System.out.println(healthScore);
		// 奖励更少的用时
		int gt = stateObs.getGameTick();

		return rawScore + 100 * healthScore - gt;
	}


}
