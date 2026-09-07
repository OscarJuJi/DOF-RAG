<template>
  <div class="login-container">
    <div class="container-form">
      <div class="information">
        <div class="info-childs">
          <h2>¡Bienvenido!</h2>
          <p>Mantengase actualizado de todas las novedades del DOF</p>
          <img alt="Vue logo" src="../assets/logo2.png" />
        </div>
      </div>

      <div class="form-information">
        <div class="form-information-childs">
          <div v-if="passwordMatch" class="password-error-message">
            <i class="bx bxs-x-circle bx-flip-horizontal"></i>
            Error: las contraseñas no coinciden
          </div>

          <h2>Cambiar Contraseña</h2>
          <p>Ingrese la nueva contraseña</p>
          <p class="instruction">
            La nueva contraseña debe contener por lo menos una letra mayúscula,
            un número y un símbolo
          </p>
          <form class="formulario-login" name="login-form">
            <div class="mb-3">
              <p class="input-description">Nueva Contraseña:</p>
              <label for="newpassword">
                <i class="bx bx-lock-alt"></i>
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="newpassword"
                  v-model="input.newPassword"
                  placeholder="Nueva Contraseña"
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
              <div v-if="capsLockOn" class="capslock-warning">
                <i class="bx bx-error-circle"></i>
                Bloqueo de mayúsculas activado
              </div>
              <div v-if="showNewPasswordError" class="error-message">
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                Ingrese una nueva contraseña
              </div>
              <div
                v-if="showPasswordLengthError"
                class="password-length-message"
              >
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                La contraseña debe tener al menos 8 caracteres
              </div>
              <div
                v-if="showPasswordStrengthMessage"
                class="password-strength-message"
              >
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                La contraseña debe contener al menos una letra mayúscula, un
                número y un símbolo
              </div>

              <p class="input-description">Validar Contraseña:</p>
              <label for="confirmPassword">
                <i class="bx bx-lock-alt"></i>
                <input
                  :type="showPassword2 ? 'text' : 'password'"
                  id="confirmPassword"
                  v-model="input.confirmPassword"
                  placeholder="Confirmar Contraseña"
                  @blur="validateConfirmPassword"
                  @keyup="checkCapsLock2"
                />
                <button
                  type="button"
                  @click="toggleShowPassword2"
                  class="password-toggle-button"
                >
                  <i
                    :class="showPassword2 ? 'bx bx-show' : 'bx bx-hide'"
                    class="password-toggle-icon"
                  ></i>
                </button>
              </label>
              <div v-if="capsLockOn2" class="capslock-warning">
                <i class="bx bx-error-circle"></i>
                Bloqueo de mayúsculas activado
              </div>
              <div v-if="showConfirmPasswordError" class="error-message">
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                Las contraseñas no coinciden
              </div>

              <hr class="linea-horizontal" />

              <input
                :disabled="!isFormValid"
                class="btn btn-outline-dark"
                value="Cambiar Contraseña"
                type="submit"
                v-on:click.prevent="changePassword()"
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
import Swal from 'sweetalert2';

export default {
  name: 'ChangePassword',

  data() {
    return {
      input: {
        newPassword: '',
        confirmPassword: '',
      },
      showNewPasswordError: false,
      showConfirmPasswordError: false,
      showPasswordStrengthMessage: false,
      showPasswordLengthError: false,
      passwordMatch: false,
      showPassword: false,
      capsLockOn: false,
      capsLockOn2: false,
      showPassword2: false,
      output: '',
    };
  },

  computed: {
    isFormValid() {
      return (
        this.input.newPassword &&
        this.input.confirmPassword &&
        !this.showPasswordLengthError &&
        !this.showPasswordStrengthMessage &&
        !this.showNewPasswordError &&
        !this.showConfirmPasswordError &&
        this.input.newPassword === this.input.confirmPassword
      );
    },
  },

  methods: {
    toggleShowPassword() {
      this.showPassword = !this.showPassword;
    },
    toggleShowPassword2() {
      this.showPassword2 = !this.showPassword2;
    },
    checkCapsLock(event) {
      this.capsLockOn =
        event.getModifierState && event.getModifierState('CapsLock');
    },
    checkCapsLock2(event) {
      this.capsLockOn2 =
        event.getModifierState && event.getModifierState('CapsLock');
    },
    changePassword() {
      if (this.isFormValid) {
        this.$router.push('/');
        axios
          .post('api/actualizar_password', {
            contraseña: this.input.newPassword,
            correo: localStorage.getItem('correo'),
          })
          .then((response) => {
            Swal.fire({
              title: 'Contraseña cambiada',
              text: response.data.message,
              icon: 'success',
              confirmButtonClass: 'custom-confirm-button-class',
              confirmButtonText: 'Aceptar',
              customClass: {
                title: 'custom-swal-title',
                content: 'custom-swal-text',
                confirmButton: 'custom-confirm-button-class',
              },
            })
              .then(() => {
                localStorage.clear();
                this.$router.push('/');
              })
              .catch(() => {});
          })
          .catch(() => {
            Swal.fire({
              title: 'Error',
              text: 'No se pudo cambiar la contraseña, intente de nuevo',
              icon: 'error',
              confirmButtonClass: 'custom-confirm-button-class',
              confirmButtonText: 'Aceptar',
              customClass: {
                title: 'custom-swal-title',
                content: 'custom-swal-text',
                confirmButton: 'custom-confirm-button-class',
              },
            });
          });
      }
    },
    validatePassword() {
      const passwordRegex =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      if (!this.input.newPassword) {
        this.showNewPasswordError = true;
      } else {
        this.showNewPasswordError = false;
      }

      if (!passwordRegex.test(this.input.newPassword)) {
        this.showPasswordStrengthMessage = true;
      } else {
        this.showPasswordStrengthMessage = false;
      }

      if (this.input.newPassword.length < 8) {
        this.showPasswordLengthError = true;
      } else {
        this.showPasswordLengthError = false;
      }
    },
    validateConfirmPassword() {
      if (this.input.newPassword !== this.input.confirmPassword) {
        this.showConfirmPasswordError = true;
      } else {
        this.showConfirmPasswordError = false;
      }
    },
  },
};
</script>

<style>
.form-information .password-error-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.instruction {
  font-size: 0.7rem;
}

.error-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.password-strength-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.password-length-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
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
</style>
