package parallel;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;

public class ParallelQuickSort extends RecursiveTask<int[]> {
	public int[] data;
	private final int p,r;

	public ParallelQuickSort(ArrayList<Integer> unsorted,int p, int r) {
		this.data = unsorted.stream().mapToInt(Integer::valueOf).toArray();
		this.p = p;
		this.r = r;
	}
	public ParallelQuickSort(int[] data,int p, int r) {
		this.data = data;
		this.p = p;
		this.r = r;
	}

	@Override
	protected int[] compute() {
		if (r > p) {
			ForkJoinTask.invokeAll(createSubtasks());
		}
		return data;
	}

	private List<ParallelQuickSort> createSubtasks() {
		List<ParallelQuickSort> subtasks = new ArrayList<>();
		int q = partition(p, r);
		subtasks.add(new ParallelQuickSort(data,p,q-1));
		subtasks.add(new ParallelQuickSort(data,q+1,r));
		return subtasks;
	}

	public int partition(int p, int r) {
		int x = data[r];
		int i = p-1;
		for (int j=p;j<r;j++){
			if (data[j]<=x) {
				i++;
				int tmp = data[i];
				data[i]=data[j];
				data[j]=tmp;
			}
		}
		int tmp = data[i+1];
		data[i+1]=data[r];
		data[r]=tmp;
		return i+1;
	}
}
