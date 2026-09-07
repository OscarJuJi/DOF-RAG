<template>
  <div class="login-container">
    <div class="container-form">
      <div class="information">
        <div class="info-childs">
          <h2>¡Bienvenido!</h2>
          <p>Manténgase actualizado de todas las novedades del DOF</p>
          <img alt="Vue logo" src="../assets/logo2.png" />
        </div>
      </div>
      <div class="form-information">
        <div class="form-information-childs">
          <h2>Iniciar Sesión</h2>
          <p>Use su correo electrónico para iniciar sesión</p>
          <form class="formulario-login" name="login-form">
            <div class="mb-3">
              <p class="input-description">Correo Electrónico:</p>
              <label for="username">
                <i class="bx bx-envelope"></i>
                <input
                  type="email"
                  id="username"
                  v-model="input.username"
                  placeholder="Correo Electrónico"
                  @blur="validateEmail"
                />
              </label>
              <div v-if="showEmailError" class="error-message">
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                Ingrese un correo válido
              </div>

              <p class="input-description">Contraseña:</p>
              <label for="password">
                <i class="bx bx-lock-alt"></i>
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  v-model="input.password"
                  placeholder="Contraseña"
                  @blur="validatePassword"
                  @keyup="checkCapsLock"
                />
                <button
                  type="button"
                  @click="toggleShowPassword"
                  class="password-toggle-button"
                >
                  <i
                    :class="showPassword ? 'bx bx-show' : 'bx bx-hide'"
                    class="password-toggle-icon"
                  ></i>
                </button>
              </label>
              <div v-if="showPasswordError" class="error-message">
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                La contraseña debe tener al menos 8 caracteres
              </div>
              <div v-if="capsLockOn" class="capslock-warning">
                <i class="bx bx-error-circle"></i>
                Bloqueo de mayúsculas activado
              </div>

              <div class="checkbox-container">
                <input
                  class="checkbox-input"
                  type="checkbox"
                  id="keep-session"
                  v-model="input.keepSession"
                />
                <span class="checkbox-text">Mantener la sesión iniciada</span>
              </div>

              <hr class="linea-horizontal" />

              <a class="forgot-password-link" href="/forgetpassword"
                >¿Contraseña Olvidada?</a
              >
              <input
                class="btn btn-outline-dark"
                :class="{ disabled: !canSubmit }"
                value="Ingresar"
                type="submit"
                :disabled="!canSubmit"
                v-on:click.prevent="login()"
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import eventBus from '../eventBus';
import { mapActions } from 'vuex';
import Swal from 'sweetalert2';

export default {
  name: 'LoginView',
  data() {
    return {
      input: {
        username: '',
        password: '',
        keepSession: false,
      },
      showEmailError: false,
      showPasswordError: false,
      showPassword: false,
      capsLockOn: false,
      output: '',
    };
  },
  computed: {
    isEmailValid() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailPattern.test(this.input.username);
    },
    isPasswordValid() {
      return this.input.password.length >= 8;
    },
    canSubmit() {
      return this.isEmailValid && this.isPasswordValid;
    },
  },
  methods: {
    ...mapActions(['updateUser']),
    validateEmail() {
      this.showEmailError = !this.isEmailValid;
    },
    validatePassword() {
      this.showPasswordError = !this.isPasswordValid;
    },
    toggleShowPassword() {
      this.showPassword = !this.showPassword;
    },
    checkCapsLock(event) {
      this.capsLockOn =
        event.getModifierState && event.getModifierState('CapsLock');
    },
    login() {
      this.validateEmail();
      this.validatePassword();

      Swal.fire({
        title: 'Iniciando Sesión',
        text: 'Por favor espere...',
        icon: 'info',
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey: false,
        customClass: {
          container: 'custom-swal-font',
          title: 'custom-swal-title',
          htmlContainer: 'custom-swal-text',
          confirmButton: 'custom-confirm-button-class',
        },
      });

      if (this.canSubmit) {
        axios
          .post('/api/login', {
            correo: this.input.username,
            contraseña: this.input.password,
            keepsesion: this.input.keepSession.toString(),
          })
          .then((response) => {
            Swal.close();
            localStorage.setItem('isAuthenticated', 'true');
            localStorage.setItem('token', response.data.token);
            axios
              .post('/api/datos_user', null, {
                params: {
                  correo: this.input.username,
                },
              })
              .then((response) => {
                this.updateUser(response.data[0]);
                localStorage.setItem('correo', this.input.username);
                eventBus.emit('user-logged-in', response.data);
              })
              .catch(() => {});
            this.$router.push('/notification-view');
          })
          .catch((error) => {
            if (error.response.status === 401) {
              Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.response.data.message,
                customClass: {
                  container: 'custom-swal-font',
                  title: 'custom-swal-title',
                  htmlContainer: 'custom-swal-text',
                  confirmButton: 'custom-confirm-button-class',
                },
              });
            } else {
              Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ha ocurrido un error inesperado, por favor vuelva a intentarlo más tarde',
                customClass: {
                  container: 'custom-swal-font',
                  title: 'custom-swal-title',
                  htmlContainer: 'custom-swal-text',
                  confirmButton: 'custom-confirm-button-class',
                },
              });
            }
          });
      }
    },
    checkAuthentication() {
      if (!localStorage.getItem('token')) {
        this.$router.push('/');
      } else {
        axios
          .post('/api/validar_token', {
            token: localStorage.getItem('token'),
          })
          .then((response) => {
            if (response.data.valid) {
              this.$router.push('/notification-view');
            } else {
              localStorage.removeItem('token');
              this.$router.push('/');
            }
          })
          .catch(() => {
            this.$router.push('/');
          });
      }
    },
  },
  created() {
    this.checkAuthentication();
  },
};
</script>

<style>
label {
  display: flex;
  align-items: center;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 5px;
  transition:
    box-shadow 0.3s,
    border-color 0.3s;
}

label:focus-within {
  border-color: #007bff;
  box-shadow: 0 0 10px #007bff;
}

input {
  border: none;
  outline: none;
  flex: 1;
  width: calc(100%);
  box-sizing: border-box;
}

input:focus {
  outline: none;
}

.password-toggle-button {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  margin-left: 10px;
}

.password-toggle-icon {
  color: #007bff;
}

.custom-confirm-button-class {
  background-color: #007bff !important;
  border-color: #007bff !important;
  color: #fff !important;
}

.custom-swal-font {
  font-family: 'Montserrat Alternates', sans-serif;
}

.custom-swal-title {
  font-family: 'Montserrat Alternates', sans-serif;
  font-weight: 700;
}

.custom-swal-text {
  font-family: 'Montserrat', sans-serif;
  font-weight: 400;
}

.error-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
  margin-bottom: 10px;
}

.capslock-warning {
  color: #eab543;
  background-color: #fff3cd;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
  margin-top: 5px;
}

.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn:enabled {
  cursor: pointer;
}
</style>
