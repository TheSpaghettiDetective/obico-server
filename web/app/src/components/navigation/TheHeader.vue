<template>
	<nav class="navbar navbar-expand-lg navbar-dark bg-dark static-top">
		<div class="container">
			<a class="navbar-brand" href="https://www.thespaghettidetective.com/">
				<img :src="logoInverted" style="height: 28px;" alt="The Spaghetti Detective" />
			</a>
			<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive"
				aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
				<span class="navbar-toggler-icon"></span>
			</button>
		<div class="collapse navbar-collapse" id="navbarResponsive">
			<ul class="navbar-nav">
				<!-- {% if user.is_authenticated %} -->
				<li class="nav-item {% if  'printers' in view_name %}active{% endif %}">
					<a class="nav-link" href="/printers/">Printer
					</a>
				</li>
				<li class="nav-item {% if  'prints' in view_name %}active{% endif %}">
					<!-- <a class="nav-link" href="/prints/">Time-lapse</a> -->
					<router-link to="/prints" class="nav-link">Time-lapse</router-link>
				</li>
				<li class="nav-item {% if  'gcodes' in view_name %}active{% endif %}">
					<a class="nav-link" href="/gcodes/">G-Code
				</a>
				</li>
				<!-- {% else %} -->
				<li class="nav-item {% if view_name == 'publictimelapse_list' %}active{% endif %}">
					<a class="nav-link glowing" href="/publictimelapses/">Spaghetti Gallery</a>
				</li>
				<!-- {% endif %} -->
				<!-- {% block nav_item_pricing %}{% endblock nav_item_pricing %} -->
				<li class="nav-item">
					<a class="nav-link" href="https://www.thespaghettidetective.com/help">Help</a>
				</li>
				<li class="nav-item">
					<a class="nav-link" href="https://discord.gg/hsMwGpD">Forum</a>
				</li>
			</ul>
			<ul class="navbar-nav ml-auto">
				<!-- {% if not user.is_authenticated %} -->
				<!-- <li class="nav-item">
					<a class="nav-link" href="/accounts/login/">Sign In</a>
				</li> -->
				<!-- {% if settings.ACCOUNT_ALLOW_SIGN_UP %} -->
				<!-- <li class="nav-item">
					<a class="nav-link" href="/accounts/signup/">Sign up</a>
				</li> -->
				<!-- {% endif %}
				{% else %} -->
				<li class="nav-item">
					<a href="/ent/subscription/#detective-hour-balance" class="nav-link badge-btn">
							<img :src="detectHourInverseImg"> 
							<span id="user-credits" class="badge badge-light">0</span>
							<!-- {{ user.dh_balance | dh_badge_num }} -->
							<span class="sr-only">Detective Hours</span>
					</a>
				</li>
				<!-- <li class="nav-item dropdown">
				<a class="nav-link dropdown-toggle user-menu" data-toggle="dropdown" href="#" id="1"
					aria-expanded="false">
					UserName
					{{user.first_name|default:user.email}}
					<span class="caret"></span></a>
				<div class="dropdown-menu dropdown-menu-right" aria-labelledby="themes">
					<a class="dropdown-item" href="/user_preferences/"><i class="fas fa-cog"></i>Preferences</a> -->
					<!-- {% block nav_item_account %}{% endblock nav_item_account %} -->
					<!-- <div class="dropdown-divider"></div>
					<a class="dropdown-item" href="/accounts/logout/"><i class="fas fa-sign-out-alt"></i>Log out</a>
				</div>
				</li> -->
				<!-- {% endif %} -->
			</ul>
		</div>
		</div>
	</nav>
</template>

<script>
import { mapState } from 'vuex'
// import logoInverted from '../../assets/img/logo-inverted.png';
import logoInverted from '../../../static/img/logo-inverted.png';
import detectHourInverseImg from '../../../static/img/detective-hour-inverse.png';
export default {
	name: "Header",
	data(){
		return{
			logoInverted,
			detectHourInverseImg
		}
	}
}
</script>

<style>

</style>