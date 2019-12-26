#include<cstdint>


enum MyEnum {
    ValueNone,
    ValueOne,
    ValueTwo
};


struct MyParameters {
    int16_t params;
    float p2;  
};

struct NestedArray {
    int16_t item[5];
    MyEnum enum_value;
};

struct MyData {
    uint16_t timestamp;
    float value;
    MyEnum enum_value;
    int16_t array[10];
    MyParameters params_array[10];
    NestedArray nested[3];
};



extern "C" {

    void MyComponent_Step(MyData const * const input,MyData  * const output);

    void MyComponent_Init(MyParameters const * const params);

}