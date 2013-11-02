#include <stdio.h>
#include <stdlib.h>
#include <time.h>
using namespace std;

bool CCW(double a, double b, double c, double d, double e, double f) {
    double det = (c*f - d*e) - (a*f - a*d) + (b*e - b*c);
    return (det > 0);
}

bool intersect(double a, double b, double c, double d, double e, double f, double g, double h) {
    if ( CCW(a, b, e, f, g, h) == CCW(c, d, e, f, g, h) ) { return false; }
    else if ( CCW(a, b, c, d, e, f) == CCW(a, b, c, d, g, h) ) { return false; }
    else { return true; }
}

int main() { 
    int n = 100000000;
    for (int i=0 ; i < n ; i++) {
        double a = rand();
        double b = rand();
        double c = rand();
        double d = rand();
        double e = rand();
        double f = rand();
        double g = rand();
        double h = rand();
        intersect(a,b,c,d,e,f,g,h);
    }

    return 0;
}
