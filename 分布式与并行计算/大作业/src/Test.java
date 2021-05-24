import consequence.*;
import parallel.*;

import java.io.*;
import java.util.ArrayList;
import java.util.concurrent.ForkJoinPool;

public class Test {
	public static void main(String[] args) throws IOException{
		ArrayList<Integer> unsorted = new ArrayList<>();

		FileReader fr = new FileReader("data/random.txt");
		BufferedReader br = new BufferedReader(fr);
		String str;
		while ((str = br.readLine())!=null) {
			String[] nums = str.split("\\s+");
			for (String num: nums)
				unsorted.add(Integer.parseInt(num));
		}

		long startTime,endTime;
		int[] result = new int[0];
		ForkJoinPool fjp = new ForkJoinPool();
		FileWriter fileWriter;
		double times = 10000;

		System.out.println("=====Serial=====");
		startTime = System.currentTimeMillis();
		for (int i=0;i<times;i++) {
			QuickSort qs = new QuickSort(unsorted);
			result = qs.sort();
			assert(result.length == unsorted.size());
		}
		endTime = System.currentTimeMillis();
		System.out.println("QuickSort: " + (endTime - startTime) / times + " ms.");
		fileWriter = new FileWriter("data/order1.txt");
		for (int i:result){fileWriter.write(i +" ");}

		startTime = System.currentTimeMillis();
		EnumerateSort es = new EnumerateSort(unsorted);
		result = es.sort();
		assert(result.length == unsorted.size());
		endTime = System.currentTimeMillis();
		System.out.println("EnumerateSort: " + (endTime - startTime) + " ms.");
		fileWriter = new FileWriter("data/order2.txt");
		for (int i:result){fileWriter.write(i +" ");}

		startTime = System.currentTimeMillis();
		for (int i=0;i<times;i++) {
			MergeSort ms = new MergeSort(unsorted);
			result = ms.sort();
			assert(result.length == unsorted.size());
		}
		endTime = System.currentTimeMillis();
		System.out.println("MergeSort: " + (endTime - startTime) / times + " ms.");
		fileWriter = new FileWriter("data/order3.txt");
		for (int i:result){fileWriter.write(i +" ");}



		System.out.println("====Parallel====");
		startTime = System.currentTimeMillis();
		for (int i=0;i<times;i++) {
			ParallelQuickSort pqs = new ParallelQuickSort(unsorted, 0, unsorted.size() - 1);
			result = fjp.invoke(pqs);
			assert(result.length == unsorted.size());
		}
		endTime = System.currentTimeMillis();
		System.out.println("QuickSort: " + (endTime - startTime) / times + " ms.");
		fileWriter = new FileWriter("data/order4.txt");
		for (int i:result){fileWriter.write(i +" ");}

		startTime = System.currentTimeMillis();
		ParallelEnumerateSort pes = new ParallelEnumerateSort(unsorted);
		result = fjp.invoke(pes);
		assert(result.length==unsorted.size());
		endTime = System.currentTimeMillis();
		System.out.println("EnumerateSort: " + (endTime - startTime) + " ms.");
		fileWriter = new FileWriter("data/order5.txt");
		for (int i:result){fileWriter.write(i +" ");}

		startTime = System.currentTimeMillis();
		for (int i=0;i<times;i++) {
			ParallelMergeSort pms = new ParallelMergeSort(unsorted);
			result = fjp.invoke(pms);
			assert(result.length == unsorted.size());
		}
		endTime = System.currentTimeMillis();
		System.out.println("MergeSort: " + (endTime - startTime) / times + " ms.");
		fileWriter = new FileWriter("data/order6.txt");
		for (int i:result){fileWriter.write(i +" ");}


//		System.out.println(unsorted.toString());
	}
}
