<template>
    <div class='printer-progress'>
      <div class="circle" :class="{active:step===0, done:step>0}">
        <font-awesome-icon icon="fa-check" />
        <p>
          {{ $t("Device Selection") }}
        </p>
      </div>
      <div class="line" :class="{active:step>=1}"></div>
      <div class="circle" :class="{active:step===1, done:step>1}">
        <font-awesome-icon :icon="['fas', 'check']" />
        <p>
          {{ $t("Install Obico") }}
        </p></div>
      <div class="line" :class="{active:step===2}"></div>
      <div class="circle" :class="{active:step===2,done:step===3}">
        <font-awesome-icon :icon="['fas', 'check']" />
        <p>
          {{ $t("Link Printer") }}
        </p></div>
    </div>
</template>
<script>
export default {
    components:{},
    props:{
      step:{
        default:0,
        type:Number
      }
    },
    data(){
        return {
        };
    },
    computed:{},
    created(){},
    mounted(){},
    watch:{},
    methods:{},
};
</script>
<style scoped lang='scss'>
.printer-progress{
  display:flex;
  align-items:center;
  justify-content: space-between;
  width:100%;
  padding:0 30px;
  .circle{
    background-color: #fff;
    border:1px solid #c6c6c6;
    width:20px;
    height:20px;
    border-radius:15px;
    position:relative;
    display:flex;
    justify-content: center;
    align-items: center;
    &.active{
      border-color:var(--color-primary);
      &:after{
        position:absolute;
        content:'';
        width:4px;
        height:4px;
        border-radius:2px;
        background-color: var(--color-primary);

      }
    }
    &.done{
      background-color:  var(--color-primary);
      border-color:var(--color-primary);
      svg{
        color:#2D3E4F
      }
    }
    p{
      position:absolute;
      bottom:-50px;
      white-space: nowrap;
    }
  }
  .line{
    flex:1;
    height:2px;
    background-color: #fff;
    &.active{
      background-color:  var(--color-primary);
    }
  }

}
</style>


