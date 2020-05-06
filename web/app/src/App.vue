<template>
	<div id="app">
		<!-- <TheHeader /> -->
		<main>
			<div id="content-wrapper" class="container">
				<transition>
					<router-view />
				</transition>
			</div>
		</main>
		<TheFooter />
	</div>
</template>
<script>
// import TheHeader from './components/navigation/TheHeader.vue';
import TheFooter from './components/navigation/TheFooter.vue';
export default {
	name: 'App',
	components:{
		// TheHeader,
		TheFooter
	}
}
</script>