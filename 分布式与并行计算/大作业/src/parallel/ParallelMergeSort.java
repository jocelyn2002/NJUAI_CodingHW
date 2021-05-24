package parallel;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;

public class ParallelMergeSort extends RecursiveTask<int[]> {
	int[] data;

	public ParallelMergeSort(ArrayList<Integer> unsorted) {
		this.data = unsorted.stream().mapToInt(Integer::valueOf).toArray();
	}
	public ParallelMergeSort(int[] unsorted) {
		this.data = unsorted;
	}

	@Override
	protected int[] compute() {
		if (data.length>1) {
			int[] data1 = new int[data.length/2];
			int[] data2 = new int[data.length - data1.length];

			System.arraycopy(data,0,data1,0, data1.length);
			System.arraycopy(data,data1.length,data2,0,data2.length);

			List<ParallelMergeSort> subtasks = new ArrayList<>();
			ParallelMergeSort t1 = new ParallelMergeSort(data1);
			ParallelMergeSort t2 = new ParallelMergeSort(data2);
			subtasks.add(t1);
			subtasks.add(t2);

			ForkJoinTask.invokeAll(subtasks);

			int i=0,j=0;
			int k = 0;
			while (i<=data1.length && j<=data2.length) {
				if (i==data1.length || (j<data2.length && data1[i] >= data2[j])) {
					data[k++]=data2[j++];
				}
				else if (j==data2.length || (i<data1.length && data1[i] < data2[j])) {
					data[k++]=data1[i++];
				}

				if (i==data1.length && j==data2.length) break;
			}
		}
		return data;
	}
}

