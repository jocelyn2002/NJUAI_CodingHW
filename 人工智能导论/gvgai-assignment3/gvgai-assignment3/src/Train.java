import java.util.Random;

import core.ArcadeMachine;
import core.game.Game;
import tools.Recorder;


public class Train
{

    public static void main(String[] args) throws Exception
    {
        Recorder recorder  = new Recorder("AliensRecorder");
        
        Game.setRecorder(recorder);
        ArcadeMachine.playOneGame( "examples/gridphysics/aliens.txt", "examples/gridphysics/aliens_lvl4.txt", null, new Random().nextInt());
    }
}
