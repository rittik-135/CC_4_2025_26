#include <iostream>
#include <vector>

using namespace std;

const int MAX_X = 1000001;
int divisors[MAX_X];

void precompute() {
    for (int i = 1; i < MAX_X; i++) {
        for (int j = i; j < MAX_X; j += i) {
            divisors[j]++;
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    precompute();

    int n;
    cin >> n;
    while (n--) {
        int x;
        cin >> x;
        cout << divisors[x] << "\n";
    }

    return 0;
}