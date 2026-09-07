<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal">
      <div class="user-container">
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
              <h2>Registro de usuario</h2>
              <p>Por favor llene los campos que se solicitan a continuación</p>
              <form class="formulario-login" name="login-form">
                <div class="mb-3">
                  <p class="input-description">Nombre(s):</p>
                  <label for="nombre">
                    <i class="bx bx-user"></i>
                    <input
                      type="text"
                      id="nombre"
                      v-model="input.nombre"
                      placeholder="Nombre(s)"
                      @blur="validateName"
                    />
                  </label>
                  <div v-if="showNameError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Campo obligatorio
                  </div>

                  <p class="input-description">Apellido paterno:</p>
                  <label for="lastname">
                    <i class="bx bx-user"></i>
                    <input
                      type="text"
                      id="appat"
                      v-model="input.apppat"
                      placeholder="Apellido paterno"
                      @blur="validateLastname"
                    />
                  </label>
                  <div v-if="showLastnameError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Campo obligatorio
                  </div>

                  <p class="input-description">Apellido Materno:</p>
                  <label for="lastnameM">
                    <i class="bx bx-user"></i>
                    <input
                      type="text"
                      id="apmat"
                      v-model="input.apmat"
                      placeholder="Apellido Materno"
                      @blur="validateLastname"
                    />
                  </label>
                  <div v-if="showLastnameMError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Campo obligatorio
                  </div>

                  <p class="input-description">Correo Electrónico:</p>
                  <label for="username">
                    <i class="bx bx-envelope"></i>
                    <input
                      type="email"
                      id="correo"
                      v-model="input.correo"
                      placeholder="Correo Electrónico"
                      @blur="validateEmail"
                    />
                  </label>
                  <div v-if="showEmailError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Ingrese un correo válido
                  </div>
                  <div v-if="showEmailError1" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Campo obligatorio
                  </div>

                  <p class="input-description">Contraseña:</p>
                  <label for="password">
                    <i class="bx bx-lock-alt"></i>
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      id="contraseña"
                      v-model="input.contraseña"
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
                    La contraseña debe tener al menos 8 caracteres, una
                    mayúscula, una minúscula y un número
                  </div>
                  <div v-if="capsLockOn" class="capslock-warning">
                    <i class="bx bx-error-circle"></i>
                    Bloqueo de mayúsculas activado
                  </div>

                  <p class="input-description">Confirmar contraseña:</p>
                  <label for="password">
                    <i class="bx bx-lock-alt"></i>
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      id="confirmPassword"
                      v-model="input.confirmPassword"
                      placeholder="Confirmar contraseña"
                      @blur="validateConfirmPassword"
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
                  <div v-if="showPasswordValidationError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Las contraseñas no coinciden
                  </div>

                  <p class="input-description">Número de teléfono:</p>
                  <label for="phone">
                    <i class="bx bx-phone"></i>
                    <input
                      type="text"
                      id="phone"
                      v-model="input.telefono"
                      placeholder="55-1234-5678"
                      @input="formatPhone"
                    />
                  </label>
                  <div v-if="showPhoneError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Campo obligatorio
                  </div>
                  <div v-if="showPhoneError1" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Ingrese un número de teléfono válido
                  </div>

                  <p class="input-description">Departamento:</p>
                  <label for="departamento" class="select-wrapper">
                    <i class="bx bx-briefcase"></i>
                    <select v-model="input.departamento" id="departamento">
                      <option value="" disabled>Seleccione una opción</option>
                      <option value="tesoreria">Tesorería</option>
                      <option value="juridico">Jurídico</option>
                      <option value="sistemas">Sistemas</option>
                      <option value="contraloria">Contraloría</option>
                      <option value="contabilidad">Contabilidad</option>
                    </select>
                  </label>
                  <div v-if="showDepartamentoError" class="error-message">
                    <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                    Campo obligatorio
                  </div>

                  <div class="checkbox-container">
                    <input
                      class="checkbox-input"
                      type="checkbox"
                      id="notifications"
                      v-model="input.notif"
                    />
                    <span class="checkbox-text"
                      >Desea recibir notificaciones de nuevos DOFs?
                    </span>
                  </div>
                  <div class="confirm">
                    <input
                      class="btn btn-outline-dark"
                      :class="{ disabled: !canSubmit }"
                      value="Registrar"
                      type="submit"
                      :disabled="!canSubmit"
                      v-on:click.prevent="create()"
                    />
                    <input
                      class="btn btn-danger"
                      value="Cancelar"
                      type="submit"
                      v-on:click.prevent="closeModal()"
                    />
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Swal from 'sweetalert2';

export default {
  name: 'RegisterView',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      input: {
        nombre: '',
        apppat: '',
        apmat: '',
        telefono: '',
        correo: '',
        contraseña: '',
        confirmPassword: '',
        notif: true,
        departamento: '',
      },
      showNameError: false,
      showLastnameError: false,
      showLastnameMError: false,
      showEmailError: false,
      showEmailError1: false,
      showPasswordError: false,
      showPasswordValidationError: false,
      showPassword: false,
      capsLockOn: false,
      showPhoneError: false,
      showPhoneError1: false,
      showDepartamentoError: false,
      output: '',
    };
  },
  computed: {
    isNameValid() {
      return this.input.nombre.trim().length > 0;
    },
    isLastnameValid() {
      return this.input.apppat.trim().length > 0;
    },
    isLastnameMValid() {
      return this.input.apmat.trim().length > 0;
    },
    isEmailValid() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailPattern.test(this.input.correo);
    },
    isEmailValid1() {
      return this.input.correo.trim().length > 0;
    },
    isPasswordValid() {
      const passwordPattern =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{};:,<.>])[a-zA-Z\d!@#$%^&*()\-_=+{};:,<.>]{8,}$/;
      return passwordPattern.test(this.input.contraseña);
    },
    isPasswordValid1() {
      return this.input.contraseña.trim().length > 0;
    },
    isPasswordValid2() {
      return this.input.contraseña === this.input.confirmPassword;
    },
    isPhoneValid() {
      const phonePattern = /^\d{2}-\d{4}-\d{4}$/;
      return phonePattern.test(this.input.telefono);
    },
    isPhoneValid1() {
      return this.input.telefono.trim().length > 0;
    },
    isDepartamentoValid() {
      return this.input.departamento.trim().length > 0;
    },
    canSubmit() {
      return (
        this.isNameValid &&
        this.isLastnameValid &&
        this.isLastnameMValid &&
        this.isEmailValid &&
        this.isPasswordValid &&
        this.isPasswordValid2 &&
        this.isPhoneValid &&
        this.isDepartamentoValid
      );
    },
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    validateName() {
      this.showNameError = !this.isNameValid;
    },
    validateLastname() {
      this.showLastnameError = !this.isLastnameValid;
    },
    validateLastnameM() {
      this.showLastnameMError = !this.isLastnameMValid;
    },
    validateEmail() {
      this.showEmailError = !this.isEmailValid;
    },
    validateEmail1() {
      this.showEmailError1 = !this.isEmailValid1;
    },
    validatePassword() {
      this.showPasswordError = !this.isPasswordValid;
    },
    validateConfirmPassword() {
      this.showPasswordValidationError = !this.isPasswordValid2;
    },
    validatePhone() {
      this.showPhoneError = !this.isPhoneValid;
    },
    validatePhone1() {
      this.showPhoneError1 = !this.isPhoneValid1;
    },
    validateDepartamento() {
      this.showDepartamentoError = !this.isDepartamentoValid;
    },
    toggleShowPassword() {
      this.showPassword = !this.showPassword;
    },
    checkCapsLock(event) {
      this.capsLockOn =
        event.getModifierState && event.getModifierState('CapsLock');
    },
    formatPhone() {
      const cleaned = this.input.telefono.replace(/\D/g, '');
      const match = cleaned.match(/^(\d{0,2})(\d{0,4})(\d{0,4})$/);
      if (match) {
        this.input.telefono = `${match[1]}${match[2] ? '-' + match[2] : ''}${
          match[3] ? '-' + match[3] : ''
        }`;
      }
    },
    checkAuthentication() {
      const isAuthenticated =
        localStorage.getItem('isAuthenticated') === 'true';
      if (isAuthenticated) {
        this.$router.push('/notification-view');
      } else {
        localStorage.removeItem('isAuthenticated');
      }
    },
    create() {
      this.validateName();
      this.validateLastname();
      this.validateLastnameM();
      this.validateEmail();
      this.validateEmail1();
      this.validatePassword();
      this.validateConfirmPassword();
      this.validatePhone();
      this.validatePhone1();
      this.validateDepartamento();

      Swal.fire({
        title: 'Registrando usuario',
        text: 'Por favor espere...',
        icon: 'info',
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey: false,
        customClass: {
          confirmButton: 'custom-confirm-button-class',
        },
      });
      const notification = this.input.notif ? '1' : '0';
      if (this.canSubmit) {
        axios
          .post('api/registro', {
            correo: this.input.correo,
            contraseña: this.input.contraseña,
            nombre: this.input.nombre,
            appat: this.input.apppat,
            apmat: this.input.apmat,
            telefono: this.input.telefono.replace(/-/g, ''),
            notif: notification,
            departamento: this.input.departamento,
          })
          .then(() => {
            Swal.close();
            Swal.fire({
              title: 'Usuario registrado',
              text: 'Usuario registrado exitosamente',
              icon: 'success',
              showConfirmButton: false,
              timer: 1500,
            });
            this.closeModal();
          })
          .catch((error) => {
            if (error.response.status === 400) {
              Swal.fire({
                icon: 'error',
                title: 'Usuario ya registrado',
                text: 'Por favor, inicie sesión',
                customClass: {
                  confirmButton: 'custom-confirm-button-class',
                },
              });
            } else {
              Swal.fire(
                'Error',
                'El correo ingresado ya se encuentra registrado. Por favor, contacte a soporte técnico.',
                'error',
              );
            }
          });
      }
    },
  },
};
</script>

<style>
.confirm {
  display: flex;
  justify-content: space-around;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.user-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: none;
}
.modal {
  background: none;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f1f1f1;
}
.error-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
}
.btn {
  background-color: #007bff;
  color: #fff;
  border: none;
  margin: 25px 0;
  cursor: pointer;
  border-radius: 4px;
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

.btn.disabled {
  background-color: #ccc;
  cursor: not-allowed;
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

.checkbox-container {
  display: flex;
  align-items: center;
  margin-bottom: 0px;
}

select {
  width: 100%;
  padding: 10px;
  border-radius: 4px;
  background-color: #fff;
  margin-top: 5px;
  font-size: 0.875rem;
  color: #495057;
  font-family: inherit;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-chevron-down' viewBox='0 0 16 16'%3E%3Cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px 16px;
}

label select {
  display: block;
  width: 100%;
  height: calc(1.5em + 0.75rem + 2px);
  padding: 0.375rem 2.25rem 0.375rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 400;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid #fff;
  border-radius: 0.375rem;
  transition:
    border-color 0.15s ease-in-out,
    box-shadow 0.15s ease-in-out;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-position: right 1rem center;
  background-size: 1rem;
}

select:focus {
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25);
}

.custom-select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.custom-select-icon {
  position: absolute;
  right: 10px;
  pointer-events: none;
}

.select-wrapper {
  position: relative;
  display: inline-block;
}

.select-wrapper select {
  width: calc(100% - 0.2rem);
  margin: 0;
  padding-right: 2rem;
  box-sizing: border-box;
  text-align: left;
}

.select-wrapper::after {
  position: absolute;
  top: 50%;
  right: 1rem;
  width: 1rem;
  height: 1rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-chevron-down' viewBox='0 0 16 16'%3E%3Cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-size: 1rem 1rem;
  transform: translateY(-50%);
  pointer-events: none;
}
</style>
