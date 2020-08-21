for _ in range(int(input())):
    n = int(input())
    l = list(map(int, input().split()))
    l.sort()
    l = l[::-1]
    ans = l[0]
    count = 0
    for i in range(1, n):
        if ans < ans | l[i]:
            ans = ans | l[i]
            count += 1


    print(count)