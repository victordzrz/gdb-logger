#include "my_component.h"

namespace
{
    float counter_;
    MyParameters params_;
}

extern "C" {

    void MyComponent_Step(MyData const * const input,MyData  * const output)
    { 
        counter_+=input->value*params_.params;
        output->value=counter_;
    }

    void MyComponent_Init(MyParameters const * const params){
        counter_=0;
        params_=*params;
    }

}