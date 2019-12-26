#include <iostream>
#include "my_component.h"

int main(){
    MyData input={0};
    MyData output={0};
    MyParameters params = {2};

    MyComponent_Init(&params);

    for (int i=0; i<2000;i++){
        input.value=i;
        MyComponent_Step(&input,&output);
        input.params_array[2].p2 = 0.25545* i;
        std::cout << output.value << "\n";
    }
    return 0;
}