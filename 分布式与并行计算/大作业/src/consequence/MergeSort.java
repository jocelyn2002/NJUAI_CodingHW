package consequence;

import java.util.ArrayList;

public class MergeSort {
	int[] unsorted;

	public MergeSort(ArrayList<Integer> unsorted) {
		this.unsorted = unsorted.stream().mapToInt(Integer::valueOf).toArray();
	}

	public int[] sort() {
		sort_data(unsorted);
		return unsorted;
	}

	private void sort_data(int[] data) {
		if (data.length==1) return;

		int[] data1 = new int[data.length/2];
		int[] data2 = new int[data.length - data1.length];

		System.arraycopy(data,0,data1,0, data1.length);
		System.arraycopy(data,data1.length,data2,0,data2.length);

		sort_data(data1);
		sort_data(data2);

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
}
