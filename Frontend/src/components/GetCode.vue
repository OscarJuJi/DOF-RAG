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
          <h2>Código de Recuperación</h2>
          <p>
            Ingrese el código de recuperación que enviamos al número
            <b> {{ phoneNumber }}: </b>
          </p>
          <form class="formulario-login" name="login-form">
            <div class="mb-3">
              <div class="code-input">
                <input
                  type="text"
                  ref="codePart1"
                  v-model="codePart1"
                  maxlength="2"
                  @input="focusNext(1)"
                  @keydown="handleBackspace(1)"
                  placeholder="XX"
                />
                <span>-</span>
                <input
                  type="text"
                  ref="codePart2"
                  v-model="codePart2"
                  maxlength="2"
                  @input="focusNext(2)"
                  @keydown="handleBackspace(2)"
                  placeholder="XX"
                />
                <span>-</span>
                <input
                  type="text"
                  ref="codePart3"
                  v-model="codePart3"
                  maxlength="2"
                  @keydown="handleBackspace(3)"
                  placeholder="XX"
                />
              </div>

              <div v-if="showCodeError" class="code-error-message">
                <i class="bx bxs-x-circle bx-flip-horizontal"></i>
                Código de recuperación inválido
              </div>

              <input
                class="btn btn-outline-dark"
                value="Validar Código"
                type="submit"
                v-on:click.prevent="validar()"
              />

              <a
                class="forgot-password-link"
                href="/forgetpassword"
                @click.prevent="solicitar"
                >Solicitar nuevo código</a
              >
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
  name: 'ForgotPassword',

  data() {
    return {
      codePart1: '',
      codePart2: '',
      codePart3: '',
      output: '',
      showCodeError: false,
      phoneNumber: 'Default',
    };
  },

  methods: {
    validar() {
      const formattedCode = `${this.codePart1}${this.codePart2}${this.codePart3}`;

      if (formattedCode.match(/^\d{2}\d{2}\d{2}$/)) {
        axios
          .post('api/validar_codigo', {
            codigo: formattedCode,
            correo: localStorage.getItem('correo'),
          })
          .then(() => {
            this.$router.push('/changepassword');
          })
          .catch(() => {
            this.showCodeError = true;
          });
      } else {
        this.showCodeError = true;
      }
    },
    focusNext(index) {
      if (index === 1 && this.codePart1.length === 2) {
        this.$refs.codePart2.focus();
      } else if (index === 2 && this.codePart2.length === 2) {
        this.$refs.codePart3.focus();
      }
    },
    handleBackspace(index) {
      if (index === 1 && this.codePart1.length === 0 && event.keyCode === 8) {
        this.$refs.codePart1.focus();
      } else if (
        index === 2 &&
        this.codePart2.length === 0 &&
        event.keyCode === 8
      ) {
        this.$refs.codePart1.focus();
      } else if (
        index === 3 &&
        this.codePart3.length === 0 &&
        event.keyCode === 8
      ) {
        this.$refs.codePart2.focus();
      }
    },
    solicitar(event) {
      axios
        .post('api/solicitar_codigo', {
          correo: localStorage.getItem('correo'),
        })
        .then((response) => {
          if (response && response.data) {
            Swal.fire({
              icon: 'success',
              title: 'Código enviado',
              text: 'Se ha mandado un nuevo código al numero de teléfono registrado',
            });
          } else {
            this.output = 'Respuesta inesperada del servidor';
          }
        })
        .catch((error) => {
          if (error.response && error.response.data) {
            this.output = error.response.data;
          } else {
            this.output = 'Error de red o servidor no disponible';
          }
        });
      if (event) {
        event.preventDefault();
      }
    },
  },
  mounted() {
    this.phoneNumber =
      localStorage
        .getItem('numero')
        .slice(3)
        .replace(/(\d{2})(\d{4})(\d{4})/, '$1 $2 $3') || 'Default';
  },
};
</script>

<style>
.code-input {
  display: flex;
  align-items: center;
  justify-content: center;
}

.code-input input {
  width: 30px;
  text-align: center;
  margin: 0 5px;
  padding: 5px;
  border: none;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  font-size: 1rem;
  font-weight: bold;
}

.code-input span {
  font-size: 1.5rem;
}

.code-error-message {
  color: #ab2a3e;
  background-color: #ffe6e6;
  padding: 5px;
  border-radius: 5px;
  font-size: 0.8rem;
  margin-top: 10px;
}
</style>
