#include <iostream>
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
    double aa[3] = { 0, 0, 1};
    double bb[3] = { 0, 0, 0};
    double cc[3] = { 0, 0, 2};
    double dd[3] = { 2, 2, 3};
    double ee[3] = {-1, 1,-1};
    double ff[3] = { 1, 0, 1};
    double gg[3] = { 2, 2, 2};
    double hh[3] = { 1, 3, 1}; 
    int n = 3;
    int i;
    for (int i=0 ; i < n ; i++) {
        cout << i << ", ";
        double a = aa[i];
        double b = bb[i];
        double c = cc[i];
        double d = dd[i];
        double e = ee[i];
        double f = ff[i];
        double g = gg[i];
        double h = hh[i];
        if (intersect(a,b,c,d,e,f,g,h)) { printf("yes\n"); }
        else { printf("no\n"); }
    }

    return 0;
}
