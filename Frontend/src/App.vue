<template>
  <router-view />
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
#app {
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  font-family: 'Calibri Alternates', Calibri;
}

body {
  margin: 0;
}

.accessibility-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  position: fixed;
  bottom: 20px;
  right: 20px;
}

.accessibility-button {
  padding: 10px 15px;
  font-size: 1rem;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.accessibility-button:hover {
  background-color: #0056b3;
}

@media screen and (max-width: 768px) {
  .accessibility-buttons {
    flex-direction: column;
    align-items: center;
  }
}

.login-container {
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  margin: 50;
}

.container-form {
  display: flex;
  border-radius: 20px;
  box-shadow: 0 5px 7px rgba(0, 0, 0, 0.1);
  min-height: 600px;
  max-width: 1000px;
  transition: all 1s ease;
  margin: 10px;
  border: solid thick black;
}

.information {
  width: 40%;
  display: flex;
  align-items: center;
  text-align: center;
  background-color: #c7eef3;
  border-top-left-radius: 20px;
  border-bottom-left-radius: 20px;
}

.info-childs {
  width: 100%;
  padding: 0 30px;
}

.info-childs h2 {
  font-size: 2.5rem;
  color: #333;
}

.info-childs p {
  margin: 15px 0;
  color: #555;
}

.form-information {
  display: flex;
  background-color: #f4f4f5;
  align-items: center;
  justify-content: center;
  width: 60%;
  text-align: center;
  border-top-right-radius: 20px;
  border-bottom-right-radius: 20px;
}

.form-information a {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
}

.form-information-childs {
  padding: 0 30px;
}

.form-password-childs {
  padding: 0 80px;
}

.form-information-childs h2 {
  color: #333;
  font-size: 2rem;
}

.form-information-childs p {
  color: #555;
}

.formulario-login {
  margin: 30px 0 0 0;
}

.formulario-login label {
  display: flex;
  align-items: center;
  border-radius: 20px;
  padding: 0 10px;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.formulario-login label input {
  width: 100%;
  padding: 10px;
  background-color: #fff;
  border: none;
  outline: none;
  border-radius: 20px;
  color: #333;
}

.formulario-login label i {
  color: #a7a7a7;
}

.checkbox-container {
  text-align: left;
  margin-top: 15px;
}

.checkbox-input {
  display: inline-block;
  margin-right: 5px;
  vertical-align: middle;
  cursor: pointer;
  width: 50px;
  height: 50px;
}

.checkbox-text {
  padding: 10px 10px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.checkbox-input[type='checkbox'] {
  appearance: none;
  width: 19px;
  height: 19px;
  border: 2px solid #007bff;
  border-radius: 5px;
  outline: none;
  cursor: pointer;
  position: relative;
  transition:
    background-color 0.3s,
    border-color 0.3s;
}

.checkbox-input:checked {
  background-color: #007bff;
  border-color: #007bff;
}

.checkbox-input:checked::before {
  content: '✔';
  color: white;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
}

.checkbox-input:hover {
  border-color: #0056b3;
}

.formulario-login input[type='submit'] {
  background-color: #0000ff;
  margin-top: 25px;
  color: #fff;
  border-radius: 20px;
  border: none;
  padding: 10px 15px;
}

.formulario-login input[type='submit']:hover {
  background-color: #000084;
}

.linea-horizontal {
  margin-top: 30px;
  margin-bottom: 10px;
  border: none;
  border-top: 1px solid #ccc;
  width: 80%;
}

.input-description {
  text-align: left;
  font-size: 0.81rem;
  margin: 10px 0;
}

.formulario-login .input-description p {
  margin-top: 20px;
}

.forgot-password-link {
  text-decoration: none;
  color: #555;
  font-weight: bold;
  font-size: 0.75rem;
  transition: color 0.3s ease;
}

.forgot-password-link:hover {
  color: #222;
}

.get-back-link {
  text-decoration: none;
  color: #555;
  font-weight: bold;
  font-size: 0.75rem;
  transition: color 0.3s ease;
}

.get-back-link:hover {
  color: #222;
}

.notification-popup {
  position: absolute;
  top: 90px;
  right: 20px;
  width: 300px;
  background-color: #fff;
  border: 1px solid #ddd;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  border-radius: 8px;
  z-index: 1000;
}

.notification-popup h3 {
  margin-top: 0;
}

.notification-popup ul {
  list-style-type: none;
  padding-left: 0;
}

.notification-popup ul li {
  margin-bottom: 10px;
}

.notification-popup ul li:last-child {
  margin-bottom: 0;
}

.user-info {
  position: absolute;
  top: 90px;
  right: 20px;
  width: 300px;
  background-color: #fff;
  border: 1px solid #ddd;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  border-radius: 8px;
  z-index: 1000;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-info .user-avatar {
  font-size: 100px;
  color: #555;
}

.user-info h2 {
  margin: 10px 0;
}

.user-info p {
  margin: 5px 0;
}

.user-actions {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.user-actions button {
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 10px;
  margin: 5px 0;
  cursor: pointer;
  border-radius: 4px;
}

.user-actions button:hover {
  background-color: #0056b3;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.5s ease;
}
.slide-left-enter,
.slide-left-leave-to {
  transform: translateX(100%);
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.5s ease;
}
.slide-right-enter,
.slide-right-leave-to {
  transform: translateX(-100%);
}

.route-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.route-enter-active {
  transition: all 0.3s ease-out;
}

.route-leave-to {
  opacity: 0;
  transform: translateX(-100px);
}

.route-leave-active {
  transition: all 0.3s ease-in;
}

@media (max-width: 768px) {
  .container-form {
    flex-direction: column;
    height: auto;
  }

  .information,
  .form-information {
    width: 100%;
    border-radius: 0;
  }

  .forgot-password-link {
    padding-bottom: 20px;
  }

  .get-back-link {
    padding-bottom: 20px;
  }

  .information {
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    margin-bottom: 0;
  }

  .form-information {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
  }

  .form-information-childs,
  .info-childs {
    padding: 20px;
  }

  .form-password-childs {
    padding: 0 20px;
  }

  .login-container {
    height: auto;
    padding: 20px 0;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .container-form {
    flex-direction: column;
    height: auto;
  }

  .information,
  .form-information {
    width: 100%;
    border-radius: 0;
  }

  .information {
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    margin-bottom: 0;
  }

  .form-information {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
  }

  .form-information-childs,
  .info-childs {
    padding: 20px;
  }

  .get-back-link {
    padding-bottom: 25px;
  }

  .form-password-childs {
    padding: 0 20px;
  }

  .login-container {
    height: auto;
    padding: 20px 0;
  }
}
</style>
