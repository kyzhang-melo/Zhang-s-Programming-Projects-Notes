# 快速排序

尽管快速排序算法对于程序员或计算机专业的学生来说非常基础，但其具有多种多样的实现方式。本文在此总结《算法导论》第7章所述的Lomuto法和Hoare法两种方法。

## Lomuto法

Lomuto法的基本思想是：选择数组的最后一个元素作为基准元素pivot，然后使用一个指针i来标记小于等于pivot元素的边界，再使用指针j遍历数组，将小于等于pivot的元素交换到指针i的左边，最后将基准元素放到正确的位置。该方法体现了快慢指针法的思想，指针 i 为慢指针，指针 j 为快指针。

算法步骤：

1. 选择数组的最后一个元素作为基准元素pivot；

2. 初始化指针i为数组的起始位置；

3. 遍历数组，对于每个元素arr[j]，如果arr[j]小于等于pivot，则将arr[j]与arr[i]交换，并将指针i向右移动一位；

4. 遍历结束，将pivot与arr[i]交换，此时pivot左边的元素都小于等于它，右边的元素都大于它；

5. 返回pivot的最终位置。

   如下所示为Lomuto法的Python语言实现：

   ``````
   def partition_Lomuto(arr, left, right):
       i = left - 1    ##指针i为慢指针
       for j in range(left, right):    ##指针j为快指针
           if arr[j] <= arr[right]:
               i += 1
               swap(arr, i, j)
       swap(arr, i + 1, right)
       return i + 1
   
   def quickSort(arr, left, right):
       if left >= right:
           return
       privot = partition_Lomuto(arr, left, right)
       quickSort(arr, left, privot - 1)    
       quickSort(arr, privot + 1, right)
   ``````

   

## Hoare法

Hoare法的基本思想是：选择数组的第一个元素作为基准元素，使用两个指针 i 和 j 分别从数组的两端开始向中间移动，指针 i 找到第一个大于等于基准元素的元素，指针 j找到第一个小于等于基准元素的元素，然后交换这两个元素，直到指针 i 和 j 相遇，最后返回基准元素的位置。该方法体现了双指针渐进法的思想，指针i为左指针，指针j为右指针。

算法步骤：

1. 选择数组的第一个元素作为基准元素pivot；

2. 初始化指针 i 为数组的起始位置，指针 j 为数组的结束位置（左右开区间）；

3. 指针 i 从左向右移动，直到找到第一个大于等于 pivot 的元素； 指针 j 从右向左移动，直到找到第一个小于等于 pivot 的元素；

4. 交换arr[i]和arr[j]；

5. 重复步骤3和4，直到指针 i 和 j 相遇；

6. 返回指针 j 的位置。

   如下所示为Hoare法的Python语言实现：

   ``````
   def partition_hoare(arr, left, right):
       x = arr[left]    ##以数组中最左元素作为pivot
       i = left - 1    ##初始化双指针，开区间法
       j = right + 1
       while True:
           i += 1
           while arr[i] < x:
               i += 1
           j -= 1
           while arr[j] > x:
               j -= 1
           if i >= j:
               return j
           swap(arr, i, j)
   
   def quickSort(arr, left, right):
       if left >= right:
           return
       privot = partition_hoare(arr, left, right)
       quickSort(arr, left, privot)
       quickSort(arr, privot + 1, right)
   ``````

   通过对比Lomuto法和Hoare法在quickSort()函数部分的代码，我们发现在子递归过程中，Lomuto法无需将pivot元素放入子数组进行递归，但Hoare法需要。这是因为Hoare法在以pivot元素进行分区结束后，数组会被划分为两部分，但这两部分并不是严格地以基准元素为界，基准元素并不一定处于其最终排序后地正确位置。而Lomuto法在分区结束后，基准元素会被放置在其最终排序后的正确位置。

   

   ## 快速排序的优化

   Lamuto法默认选取数组的最后一个元素作为pivot元素，Hoare法默认选取数组的第一个元素作为pivot元素。在极端情况下（例如pivot元素恰好是数组中的最大值或最小值），会导致快速排序算法的时间复杂度由$O(nlogn)$ 升至 $O(n^2)$。但如果要从无序数组中找到接近中间值的元素，又是比较困难的。因此，需要在pivot元素的选择过程中加入一些随机性。考虑到随机数生成器也会消耗一些运行时间，故本人倾向于使用三值取中法，选取pivot元素。优化后的代码如下所示：

   ``````
   def medianin3 (arr, left, middle, right):
       l = arr[left]
       m = arr[middle]
       r = arr[right]
       if (l <= m and m <= r) or (l >= m and m >= r):
           return middle
       if (m <= l and l <= r) or (m >= l and l >= r):
           return left
       return right
   
   ##Lomuto法
   def partition_Lomuto(arr, left, right):
       mid = medianin3(arr, left, left + int((right - left)/2), right)
       swap(arr, mid, right)    ##以最右元素作为哨兵
       i = left - 1
       for j in range(left, right):
           if arr[j] <= arr[right]:
               i += 1
               swap(arr, i, j)
       swap(arr, i + 1, right)
       return i + 1
   
   def quickSort_Lomuto(arr, left, right):
       if left >= right:
           return
       privot = partition_Lomuto(arr, left, right)
       quickSort(arr, left, privot - 1)    ##pivot元素无需放入子数组进行递归
       quickSort(arr, privot + 1, right)
   
   ##Hoare法
   def partition_hoare(arr, left, right):
       mid = median3(arr, left, left + int((right - left)/2), right)
       swap(arr, mid, left)    ##以最左元素作为哨兵
       x = arr[left]
       i = left - 1
       j = right + 1
       while True:
           i += 1
           while arr[i] < x:
               i += 1
           j -= 1
           while arr[j] > x:
               j -= 1
           if i >= j:
               return j
           swap(arr, i, j)
   
   def quickSort_Hoare(arr, left, right):
       if left >= right:
           return
       privot = partition_hoare(arr, left, right)
       quickSort(arr, left, privot)    ##pivot元素需放入子数组进行递归
       quickSort(arr, privot + 1, right)
   ``````

   值得注意的是，Hoare法在很多情况下比Lomuto法要更快，因为Hoare法的交换次数更少、交换频率更低。Hoare于1962年发表在《The Computer Journal》的《Quicksort》一文(https://doi.org/10.1093/comjnl/5.1.10）值得一读。

   