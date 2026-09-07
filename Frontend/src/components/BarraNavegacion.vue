<template>
  <div class="barra">
    <nav class="navbar welcome-navbar">
      <div class="contenedor-barras">
        <div class="navbar-brand">
          <span class="navbar-item left">
            <a class="link" href="/notification-view">
              <img src="../assets/logo.png" alt="Romboworks" />
            </a>
          </span>
          <div class="navbar-burger" @click="toggleMenu">
            <i class="bx bx-menu"></i>
          </div>
          <div class="navbar-menu-1" :class="{ 'is-active': menuActive }">
            <div class="navbar-end">
              <div class="navbar-item">
                <a class="link" href="/notification-view">Novedades</a>
              </div>
              <div class="navbar-item">
                <a class="link" href="/consult-view">Consultas</a>
              </div>
              <div class="navbar-item">
                <a class="link" href="/resumen-view">Resúmenes</a>
              </div>
              <div class="navbar-item" v-if="user && user.rol === 'admin'">
                <a class="link" href="/employees-view">Empleados</a>
              </div>
            </div>
          </div>
          <div class="navbar-icons">
            <div class="navbar-item icon" @click="toggleUserMenu">
              <i class="bx bx-user-circle"></i>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <div class="navbar-menu" :class="{ 'is-active': menuActive }">
      <div class="navbar-end">
        <div class="navbar-item">
          <a class="link" href="/notification-view">Novedades</a>
        </div>
        <div class="navbar-item">
          <a class="link" href="/consult-view">Consultas</a>
        </div>
        <div class="navbar-item">
          <a class="link" href="/resumen-view">Resúmenes</a>
        </div>
        <div class="navbar-item" v-if="user && user.rol === 'admin'">
          <a class="link" href="/employees-view">Empleados</a>
        </div>
      </div>
    </div>

    <div class="welcome-text">
      <div class="text-container">
        <h1>{{ welcomeMessage }}</h1>
      </div>
    </div>

    <div v-if="showNotifications" class="modal-overlay" @click="closeModal">
      <div class="notification-popup" @click.stop>
        <h3>Notificaciones</h3>
        <ul>
          <li>Notificación 1: Detalle de la notificación 1</li>
          <li>Notificación 2: Detalle de la notificación 2</li>
          <li>Notificación 3: Detalle de la notificación 3</li>
        </ul>
      </div>
    </div>

    <div v-if="showUserMenu" class="modal-overlay" @click="closeModal">
      <div class="user-info" @click.stop>
        <i class="bx bx-user-circle user-avatar"></i>
        <h2>{{ user.nombre }}</h2>
        <p><strong>Correo:</strong> {{ user.correo }}</p>
        <p><strong>Teléfono:</strong> {{ user.telefono }}</p>
        <div class="user-actions">
          <button @click="toggleEditModal">Modificar Datos</button>
          <button @click="logout">Cerrar Sesión</button>
        </div>
      </div>
    </div>

    <div v-if="showHelpModal" class="modal-overlay" @click="closeModal">
      <div class="notification-popup" @click.stop>
        <div class="slides">
          <div
            class="slide"
            v-for="(slide, index) in slides"
            :key="index"
            v-show="currentSlide === index"
          >
            <h3>{{ slide.title }}</h3>
            <p>{{ slide.content }}</p>
          </div>
        </div>
        <div class="slide-indicators">
          <span
            v-for="(slide, index) in slides"
            :key="index"
            :class="{ active: currentSlide === index }"
            @click="setSlide(index)"
          ></span>
        </div>
        <div class="slide-controls">
          <i class="bx bx-chevron-left" @click="previousSlide"></i>
          <i class="bx bx-chevron-right" @click="nextSlide"></i>
        </div>
        <button
          v-if="currentSlide === slides.length - 1"
          @click="toggleHelpModal"
        >
          Cerrar
        </button>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay1" @click="toggleEditModal">
      <div class="modal-content" @click.stop>
        <i class="bx bx-user-circle user-avatar"></i>
        <h3>Modificar Datos del Usuario</h3>
        <form @submit.prevent="updateUser">
          <div class="contenedorNombre">
            <div class="field">
              <p>Nombre</p>
              <div class="control">
                <input
                  class="user-input"
                  type="text"
                  v-model="editedUser.nombre"
                  required
                />
              </div>
            </div>
            <div class="field">
              <p>Apellido paterno</p>
              <div class="control">
                <input
                  class="user-input"
                  type="text"
                  v-model="editedUser.appat"
                  required
                />
              </div>
            </div>
            <div class="field">
              <p>Apellido materno</p>
              <div class="control">
                <input
                  class="user-input"
                  type="text"
                  v-model="editedUser.apmat"
                  required
                />
              </div>
            </div>
          </div>
          <div class="contenedorTelefono">
            <p>Teléfono</p>
            <div class="control2">
              <input
                class="user-input"
                type="text"
                v-model="editedUser.telefono"
                required
              />
            </div>
          </div>
          <div class="contenedorTelefono">
            <p>Recibir notificaciones</p>
            <div class="control3">
              <label class="switch">
                <input
                  type="checkbox"
                  v-model="editedUser.notif"
                  true-value="true"
                  false-value="false"
                />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="botonesMid">
            <div class="field">
              <button type="submit" :disabled="loading" @click="updateUser">
                <span v-if="loading">
                  <i class="bx bx-loader bx-spin"></i> Guardando...
                </span>
                <span v-else> Guardar </span>
              </button>
            </div>
            <div class="field">
              <button @click="toggleEditModal">Cancelar</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import eventBus from '../eventBus';
import { mapGetters } from 'vuex';
import Swal from 'sweetalert2';

export default {
  props: ['welcomeMessage'],
  data() {
    return {
      showNotifications: false,
      showUserMenu: false,
      menuActive: false,
      showHelpModal: false,
      showEditModal: false,
      currentSlide: 0,
      loading: false,
      editedUser: {
        nombre: '',
        appat: '',
        apmat: '',
        telefono: '',
        notif: true,
      },
      slides: [
        { title: 'Ayuda 1', content: 'Contenido de ayuda 1' },
        { title: 'Ayuda 2', content: 'Contenido de ayuda 2' },
        { title: 'Ayuda 3', content: 'Contenido de ayuda 3' },
        { title: 'Ayuda 4', content: 'Contenido de ayuda 4' },
      ],
    };
  },
  computed: {
    ...mapGetters(['user']),
  },
  watch: {
    user(newUser) {
      this.editedUser = { ...newUser };
    },
  },
  methods: {
    closeModal(event) {
      if (event.target.classList.contains('modal-overlay')) {
        this.showNotifications = false;
        this.showUserMenu = false;
        this.showHelpModal = false;
        this.showEditModal = false;
      }
    },
    toggleNotification() {
      this.showNotifications = !this.showNotifications;
    },
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    toggleMenu() {
      this.menuActive = !this.menuActive;
    },
    toggleHelpModal() {
      this.showHelpModal = !this.showHelpModal;
    },
    toggleEditModal() {
      this.showEditModal = !this.showEditModal;
      if (this.showEditModal) {
        this.editedUser = { ...this.user };
      }
    },
    previousSlide() {
      this.currentSlide =
        this.currentSlide > 0 ? this.currentSlide - 1 : this.slides.length - 1;
    },
    nextSlide() {
      this.currentSlide =
        this.currentSlide < this.slides.length - 1
          ? this.currentSlide + 1
          : this.slides.length - 1;
    },
    setSlide(index) {
      this.currentSlide = index;
    },
    handleResize() {
      if (window.innerWidth > 768 && this.menuActive) {
        this.menuActive = false;
      } else if (window.innerWidth < 1024) {
        this.menuActive = false;
      }
    },
    logout() {
      localStorage.removeItem('isAuthenticated');
      this.$store.dispatch('updateUser', {
        nombre: '',
        correo: '',
        telefono: '',
        area: '',
        rol: '',
        notif: 0,
      });
      localStorage.removeItem('token');
      location.reload();
    },
    updateUser() {
      this.loading = true;
      axios
        .post('/api/actualizar_user', this.editedUser)
        .then(() => {
          this.$store.dispatch('updateUser', this.editedUser);
          this.toggleEditModal();
          Swal.fire({
            title: 'Datos actualizados',
            text: 'Los datos del usuario han sido actualizados correctamente',
            icon: 'success',
            confirmButtonText: 'Aceptar',
            customClass: {
              container: 'custom-swal-font',
              title: 'custom-swal-title',
              htmlContainer: 'custom-swal-text',
              confirmButton: 'custom-confirm-button-class',
            },
          });
          this.loading = false;
        })
        .catch(() => {
          Swal.fire({
            title: 'Error al actualizar',
            text: 'Ha ocurrido un error al actualizar los datos del usuario',
            icon: 'error',
            confirmButtonText: 'Aceptar',
            customClass: {
              container: 'custom-swal-font',
              title: 'custom-swal-title',
              htmlContainer: 'custom-swal-text',
              confirmButton: 'custom-confirm-button-class',
            },
          });
          this.loading = false;
        });
    },
  },
  created() {
    window.addEventListener('resize', this.handleResize);
    eventBus.on('user-logged-in', this.updateUser);
  },
  beforeUnmount() {
    eventBus.off('user-logged-in', this.updateUser);
    window.removeEventListener('resize', this.handleResize);
  },
};
</script>

<style>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: none;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-overlay1 {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  display: flex;
  background: white;
  color: black;
  border-radius: 8px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  width: 80%;
  max-width: 600px;
  overflow: auto;
  max-height: 80%;
}
.contenedorNombre {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
}
.contenedorTelefono {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 20px;
}

form {
  width: 80%;
}
.botonesMid {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  padding-top: 20px;
}

.barra .welcome-navbar {
  background-color: #fff;
  color: #fff;
  width: 100%;
}

.welcome-navbar .contenedor-barras {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.navbar-item a {
  text-decoration: none;
  color: #555;
  font-weight: bold;
  font-size: 1.2rem;
}

.navbar-item a:hover {
  color: #222;
}

.welcome-navbar .navbar-brand,
.welcome-navbar .navbar-item {
  display: flex;
  align-items: center;
}

.welcome-navbar .navbar-item.left {
  margin-right: auto;
}

.welcome-navbar .navbar-item {
  text-decoration: none;
  margin-left: 20px;
}

.welcome-navbar .navbar-end {
  display: flex;
  align-items: center;
}

.welcome-navbar .navbar-brand {
  padding-top: 20px;
  padding-bottom: 20px;
}

.navbar-burger {
  display: none;
  cursor: pointer;
  font-size: 35px;
  color: #555;
}

.navbar-icons {
  display: flex;
  align-items: center;
  margin-left: 20px;
}

.navbar-icons .icon {
  margin-left: 10px;
}

.navbar-menu.is-active {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.navbar-menu {
  display: none;
}

.slides {
  position: relative;
  height: 200px;
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.5s;
}

.slide-indicators {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.slide-indicators span {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin: 0 5px;
  background: #ccc;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s;
}

.slide-indicators span.active {
  background: #333;
}

.slide:nth-child(even) {
  background-color: #f9f9f9;
}

.slide:nth-child(odd) {
  background-color: #f1f1f1;
}

.slide-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
}

.slide-controls i {
  font-size: 24px;
  margin: 0 10px;
  cursor: pointer;
}

.slide-controls i:hover {
  color: #555;
}

.modal-content button {
  margin-top: 10px;
  padding: 10px 20px;
  border: none;
  background: #007bff;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}

.modal-content button:hover {
  background: #0056b3;
}

.control {
  margin-top: 0.5rem;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 5px;
  transition:
    box-shadow 0.3s,
    border-color 0.3s;
}
.control:focus-within {
  border-color: #007bff;
  box-shadow: 0 0 10px #007bff;
}

.control2 {
  margin-top: 0.5rem;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 5px;
  width: 150px;
  transition:
    box-shadow 0.3s,
    border-color 0.3s;
  margin-left: 10px;
}
.control2:focus-within {
  border-color: #007bff;
  box-shadow: 0 0 10px #007bff;
}

.control3 {
  margin-top: 0.5rem;
  border: none;
  border-radius: 5px;
  width: 150px;
  transition:
    box-shadow 0.3s,
    border-color 0.3s;
  margin-left: 10px;
}

.user-input {
  border: none;
  outline: none;
  flex: 1;
  width: calc(100%);
  box-sizing: border-box;
}

input:focus {
  outline: none;
}

.is-grouped .control {
  margin-right: 1rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: '';
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4caf50;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.user-avatar {
  margin-bottom: 30px;
  font-size: 150px;
}
</style>
