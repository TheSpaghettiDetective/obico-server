<template>
	<div class="timelapse-gallery">
		<div class="row my-5 justify-content-center">
			<div class="col-12">
				<a role="button" class="btn btn-outline-primary btn-block" href="/prints/upload/">
					Upload time-lapses and earn some 
					<img class="dh-icon" :src="detectHourPrimaryImg" />
				</a>
			</div>
		</div>
		<form id="prints-form" method="POST" ></form>
		<div class="row">
			<div class="col-sm-12 text-center pb-3">
				<button type="button" id="delete-prints-btn" class="btn btn-light float-right ml-3" disabled><i
					class="fas fa-trash-alt"></i> Delete</button>
				<button type="button" id="select-all-btn" class="btn btn-primary float-right">Select All</button>
			</div>
		</div>
	</div>
</template>

<script>
import detectHourPrimaryImg from '../assets/img/detective-hour-primary.png';
export default {
	name: 'prints',
	data(){
		return{
			detectHourPrimaryImg
		}
	}
}
</script>

<style>

</style>