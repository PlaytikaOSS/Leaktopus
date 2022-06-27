<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light sticky-top mb-5">
    <div class="container-fluid px-0">
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <router-link class="nav-link" active-class="active" to="/">Scans</router-link>
                </li>
                <li class="nav-item">
                    <router-link class="nav-link" active-class="active" to="/github-preferences">GitHub Preferences</router-link>
                </li>
            </ul>
        </div>
    </div>
  </nav>
  <router-view/>
</template>

<style>
/* Main styles */
body {
	font-family: 'Kanit', sans-serif !important;
	margin: auto;
}
body .padding-top {
	padding-top: 0rem !important;
}

header {
    position: relative;
    height: 180px;
    background-color: #0062cc;
}

h1 {
    letter-spacing: -.13px;
    text-transform: uppercase;
    font-size: 40px !important;
	font-weight: 800 !important;
	font-style: italic;
    text-align: center;
}

.logo img {
    height: 45px;
}

@media only screen and (min-width: 1200px) {
	header {
		height: 150px;
		background-size: auto 150px;
		margin-bottom: 30px;
	}

	h1 {
		position: absolute;
		top: 0;
		width: 100%;
		font-size: 68px !important;
		line-height: 150px !important;
		color: #FFF;
		text-shadow: -5px 5px #007bff;
	}

	.logo { padding-bottom: 25px; }

	.logo img { height: 150px; }

	.footer-decor { max-width: 100px; }
}

.waves {
	position:absolute;
	bottom: 0;
	width: 100%;
	height:15vh;
	margin-bottom:-7px; /*Fix for safari gap*/
	min-height:40px;
	max-height:60px;
}

/* Animation */

.parallax > use {
	animation: move-forever 25s cubic-bezier(.55,.5,.45,.5)     infinite;
}
.parallax > use:nth-child(1) {
	animation-delay: -2s;
	animation-duration: 7s;
}
.parallax > use:nth-child(2) {
	animation-delay: -3s;
	animation-duration: 10s;
}
.parallax > use:nth-child(3) {
	animation-delay: -4s;
	animation-duration: 13s;
}
.parallax > use:nth-child(4) {
	animation-delay: -5s;
	animation-duration: 20s;
}
@keyframes move-forever {
	0% {
		transform: translate3d(-90px,0,0);
	}
	100% {
		transform: translate3d(85px,0,0);
	}
}

[v-cloak] {
  display: none;
}
</style>
