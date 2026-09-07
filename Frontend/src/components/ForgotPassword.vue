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
        <div class="form-password-childs">
          <h2>¿Olvidó su contraseña?</h2>
          <p>
            Ingrese el correo electrónico asociado a su cuenta para recuperar la
            contraseña
          </p>
          <form class="formulario-login" @submit.prevent="solicitar">
            <div class="restore-pass">
              <p class="input-description">Correo Electrónico:</p>
              <label for="username" :class="{ error: showEmailError }">
                <i class="bx bx-envelope"></i>
                <input
                  type="email"
                  id="username"
                  v-model.trim="input.username"
                  placeholder="Correo Electrónico"
                  @blur="validateEmail"
                  @input="validateEmail"
                />
              </label>
              <div v-if="showEmailError" class="error-message">
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                {{ output }}
              </div>
            </div>

            <hr class="linea-horizontal" />
            <input
              class="btn btn-outline-dark"
              :class="{ disabled: !canSubmit }"
              value="Enviar Código"
              type="submit"
              :disabled="!canSubmit"
            />

            <a class="get-back-link" href="/">Regresar a Inicio de Sesión</a>
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
  name: 'ForgotPassword',

  data() {
    return {
      input: {
        username: '',
      },
      showEmailError: false,
      output: '',
    };
  },
  computed: {
    isEmailNotEmpty() {
      return this.input.username !== '';
    },
    isEmailValid() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailPattern.test(this.input.username);
    },
    canSubmit() {
      return this.isEmailNotEmpty && this.isEmailValid;
    },
  },

  methods: {
    validateEmail() {
      if (!this.isEmailNotEmpty || !this.isEmailValid) {
        this.showEmailError = true;
        this.output = 'Ingrese un correo electrónico válido';
      } else {
        this.showEmailError = false;
        this.output = '';
      }
    },
    solicitar() {
      this.validateEmail();
      if (this.canSubmit) {
        axios
          .post('api/solicitar_codigo', {
            correo: this.input.username,
          })
          .then((response) => {
            localStorage.setItem('correo', this.input.username);
            localStorage.setItem('numero', response.data.message);
            this.$router.push('/verificate-code');
          })
          .catch((error) => {
            Swal.fire({
              icon: 'error',
              title: 'Error',
              text: error.response.data.message,
            });
          });
      }
    },
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

label.error {
  border-color: #ab2a3e;
}

label:focus-within {
  border-color: #007bff;
  box-shadow: 0 0 10px #007bff;
}

.restore-pass input {
  border: none;
  outline: none;
  flex: 1;
}

.restore-pass input:focus {
  outline: none;
}

.error-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.btn:enabled {
  cursor: pointer;
}
.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
