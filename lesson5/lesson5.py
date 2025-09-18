import random

step = random.randint(3, 5)
arr = list(range(10, 250_000_000, step))

random_numbers = [random.randint(10, 250_000_000) for _ in range(10)]

def linear_search(arr, target):
    for i, value in enumerate(arr):
        if value == target:
            return i  # нашли индекс
    return -1  # не нашли

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

import time

for num in random_numbers:
    # Линейный поиск
    start = time.time()
    idx_lin = linear_search(arr, num)
    end = time.time()
    print(f"Линейный поиск: {num} {'найден' if idx_lin != -1 else 'не найден'} за {end - start:.6f} сек.")

    # Бинарный поиск
    start = time.time()
    idx_bin = binary_search(arr, num)
    end = time.time()
    print(f"Бинарный поиск: {num} {'найден' if idx_bin != -1 else 'не найден'} за {end - start:.6f} сек.")
    print("-" * 50)

###

import random

arr1 = [random.randint(1, 1_000_000) for _ in range(100_000)]

arr2 = [
    {"num_1": random.randint(1, 1_000_000), "num_2": random.randint(1, 1_000_000)}
    for _ in range(100_000)
]

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        # оптимизация: если не было обменов — список уже отсортирован
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# сортировка первого массива
sorted_arr1 = bubble_sort(arr1[:])  # [:] чтобы не портить оригинал

arr2.sort(key=lambda d: (d["num_1"], d["num_2"]))