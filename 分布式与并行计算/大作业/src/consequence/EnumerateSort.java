package consequence;

import java.util.ArrayList;

public class EnumerateSort {
	int[] unsorted,sorted;

	public EnumerateSort(ArrayList<Integer> unsorted) {
		this.unsorted = unsorted.stream().mapToInt(Integer::valueOf).toArray();
		sorted = new int[unsorted.size()];
	}

	public int[] sort() {
		for (int i=0;i<unsorted.length;i++) {
			int counter = 0;
			for (int j=0;j<unsorted.length;j++) {
				if (j==i) continue;
				if (unsorted[j]<unsorted[i]) counter++;
			}
			sorted[counter] = unsorted[i];
		}
		return sorted;
	}
}
