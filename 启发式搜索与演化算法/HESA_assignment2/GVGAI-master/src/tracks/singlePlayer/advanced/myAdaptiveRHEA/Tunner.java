package tracks.singlePlayer.advanced.myAdaptiveRHEA;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Random;

public class Tunner {
	// Parameter
	private int L = 3; // 1 - 10
	private int CROSSOVER_TYPE = 0; // 0,1
	private int MUTATION = 2; // 0-4
	private int TOURNAMENT_SIZE = 4; // 2-4
	private int ELITISM = 1; // 0-4


	private int[][] population, nextPop;
	private Random rand;
	private int[] tmp;
	private int Popnum = 10;


	public Tunner() {
		population = new int[Popnum][6];
		for (int i=0;i<Popnum;i++)
			population[i] = new int[]{L,CROSSOVER_TYPE, MUTATION,TOURNAMENT_SIZE,ELITISM,0};
		rand = new Random();
	}

	public boolean flip_a_coin() {
		return rand.nextInt(100) > 95;
	}

	public int[] getParameters(){
		Arrays.sort(population, Comparator.comparingDouble(x -> x[5]));
		tmp = population[0].clone();
		if (flip_a_coin()) tmp[0] = 1 + rand.nextInt(10);
		if (flip_a_coin()) tmp[1] = rand.nextInt(2);
		if (flip_a_coin()) tmp[2] = rand.nextInt(5);
		if (flip_a_coin()) tmp[3] = 2 + rand.nextInt(3);
		if (flip_a_coin()) tmp[4] = rand.nextInt(5);
//		if (tmp[5]!=0)
			System.out.println(Arrays.toString(tmp));
		return tmp;
	}

	public void UpdateParameters(int score) {
		tmp[5] = score;
		if (tmp[5] > population[Popnum-1][5]) population[Popnum-1] = tmp.clone();
	}
}
