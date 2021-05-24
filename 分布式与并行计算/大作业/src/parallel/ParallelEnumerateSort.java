package parallel;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;

public class ParallelEnumerateSort extends RecursiveTask<int[]> {
	int[] unsorted,sorted;
	int number;

	public ParallelEnumerateSort(ArrayList<Integer> unsorted) {
		this.unsorted = unsorted.stream().mapToInt(Integer::valueOf).toArray();
		this.sorted = new int[unsorted.size()];
		this.number = -1;
	}
	public ParallelEnumerateSort(int[] unsorted,int[] sorted,int i) {
		this.unsorted = unsorted;
		this.sorted = sorted;
		this.number = i;
	}

	@Override
	protected int[] compute() {
		if (number==-1) {
			List<ParallelEnumerateSort> subtasks = new ArrayList<>();
			for (int i=0;i<unsorted.length;i++) {
				ParallelEnumerateSort new_t = new ParallelEnumerateSort(unsorted,sorted,i);
				subtasks.add(new_t);
			}
			ForkJoinTask.invokeAll(subtasks);
		}
		else {
			int counter = 0;
			for (int i=0;i<unsorted.length;i++) {
				if (i==number) continue;
				if (unsorted[i]<unsorted[number]) counter++;
			}
			sorted[counter] = unsorted[number];
		}
		return sorted;
	}
}
