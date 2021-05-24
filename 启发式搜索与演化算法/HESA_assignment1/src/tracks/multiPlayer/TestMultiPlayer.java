package tracks.multiPlayer;
import java.util.Random;
import core.logging.Logger;
import tools.Utils;
import tracks.ArcadeMachine;

public class TestMultiPlayer {
	public static void main(String[] args) {
		// 一些可用的控制器
		String doNothingController = "tracks.multiPlayer.simple.doNothing.Agent";
		String randomController = "tracks.multiPlayer.simple.sampleRandom.Agent";
		String oneStepController = "tracks.multiPlayer.simple.sampleOneStepLookAhead.Agent";
		String sampleMCTSController = "tracks.multiPlayer.advanced.sampleMCTS.Agent";
		String sampleRSController = "tracks.multiPlayer.advanced.sampleRS.Agent";
		String sampleRHEAController = "tracks.multiPlayer.advanced.sampleRHEA.Agent";
		String humanController = "tracks.multiPlayer.tools.human.Agent";
		String myController = "tracks.multiPlayer.my.Agent";

		// 可以在这里设置游戏中的控制器，如果要自己玩，可以把其中一个控制器改为humanController，自己就可以控制相应的agent
		String controllers = myController + " " + myController;
//
		boolean visuals = true;
		String recordActionsFile = null;
		// 随机种子的设置
//		int seed = new Random().nextInt(); // 你可以使用随机种子
		int seed = 2020; // 最终运行的时候你需要固定种子
		int levelIdx = 2; // 选择游戏关卡，从0到4一共5关
		String gameName = "pacoban";
		String game = "examples/pacoban.txt";
		String level1 = game.replace(gameName, gameName + "_lvl" + levelIdx);
//		 1. 玩一轮可视化的游戏
		ArcadeMachine.runOneGame(game, level1, visuals, controllers, recordActionsFile, seed, 1);
//		 2. 在前N关，玩M次:
//		int N = 3;
//		int M = 3;
//		for (int i = 0; i <= N; i++) {
//			level1 = game.replace(gameName, gameName + "_lvl" + i);
//			ArcadeMachine.runGames(game, new String[]{level1}, M, controllers, null);
//		}
		// 每一关会返回结果，即四个数：前两个数表示哪个玩家胜利了，后两个数表示在M次运行的平均分数；
		// 我们关注的是玩家0和玩家1的总分数要高，报告中的分数也是两位玩家的分数和。
	}
}
