package consequence;

import java.util.ArrayList;

public class QuickSort {
	int[] data;

	public QuickSort(ArrayList<Integer> unsorted) {
		data = unsorted.stream().mapToInt(Integer::valueOf).toArray();
	}

	public int[] sort() {
		return sort(0,data.length-1);
	}

	public int[] sort(int p, int r) {
		if (p<r) {
			int q = partition(p, r);
			sort(p, q - 1);
			sort(q + 1, r);
		}
		return data;
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
