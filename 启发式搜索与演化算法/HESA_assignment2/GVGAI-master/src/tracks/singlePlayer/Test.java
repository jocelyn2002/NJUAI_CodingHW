package tracks.singlePlayer;

import java.util.Random;

import tools.Utils;
import tracks.ArcadeMachine;

/**
 * Created with IntelliJ IDEA. User: Diego Date: 04/10/13 Time: 16:29 This is a
 * Java port from Tom Schaul's VGDL - https://github.com/schaul/py-vgdl
 */
public class Test {

    public static void main(String[] args) {
		String mcts = "tracks.singlePlayer.advanced.sampleMCTS.Agent";
        String rs = "tracks.singlePlayer.advanced.sampleRS.Agent";
        String rhea = "tracks.singlePlayer.advanced.sampleRHEA.Agent";
		String my = "tracks.singlePlayer.advanced.myRHEA.Agent";
		String myAdaptive = "tracks.singlePlayer.advanced.myAdaptiveRHEA.Agent";

		//Load available games
		String spGamesCollection =  "examples/all_games_sp.csv";
		String[][] games = Utils.readGames(spGamesCollection);

		int seed = new Random().nextInt();

		// Game and level to play
		int gameIdx = 112;
		String algorithm = myAdaptive;
		for (int levelIdx = 0;levelIdx<=4;levelIdx++) {
			String gameName = games[gameIdx][1];
			String game = games[gameIdx][0];
			String level1 = game.replace(gameName, gameName + "_lvl" + levelIdx);
			ArcadeMachine.runOneGame(game, level1, true, algorithm, null, seed, 0);
		}
    }
}
