// Views
import Prints from '../views/prints.vue';

export const routes = [
    {
        path : '/',
        name: 'home'
    },
    {   
        path : '/prints',
        name: 'prints',
        components:{
            default: Prints
        }
    }
];