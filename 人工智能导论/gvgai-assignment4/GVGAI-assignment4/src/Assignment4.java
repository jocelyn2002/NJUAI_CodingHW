import java.lang.annotation.Repeatable;
import java.util.Random;
import core.competition.CompetitionParameters;

import core.ArcadeMachine;

/**
 * Created with IntelliJ IDEA.
 * User: Diego
 * Date: 04/10/13
 * Time: 16:29
 * This is a Java port from Tom Schaul's VGDL - https://github.com/schaul/py-vgdl
 */
public class Assignment4
{

    public static void main(String[] args)
    {
        //Reinforcement learning controllers:
    	String rlController = "controllers.learningmodel.Agent";
        
        //Only freeway game
        String game = "examples/gridphysics/freeway.txt";
        String level = "examples/gridphysics/freeway_lvl";

        //Other settings
        boolean visuals = true;
        int seed = new Random().nextInt();

        CompetitionParameters.ACTION_TIME = 1000000;
        for(int i=0; i<10; i++){
            String levelfile = level + "3.txt";
            ArcadeMachine.runOneGame(game, levelfile, visuals, rlController, null, seed, false);
        }
        
    }
}
