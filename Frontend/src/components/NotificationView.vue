<template>
  <div class="clase">
    <BarraNavegacion :welcomeMessage="welcomeMessage" />

    <div class="main-content">
      <div class="main-left">
        <h2>Normas de tu itneres con cambios recientes</h2>
        <ul>
          <li>
            <strong
              >Cambio en los lineamientos emitidos por la Unidad de Inteligencia
              Financiera</strong
            >
          </li>
          <p>
            Para reportar operaciones sospechosas a la Unidad de Inteligencia
            Financiera (UIF) en México, se debe seguir el siguiente
            procedimiento: <br />
            1. Identificar la operación sospechosa: Reconocer cualquier
            transacción o actividad financiera que pueda estar relacionada con
            lavado de dinero, financiamiento al terrorismo u otras actividades
            ilícitas. <br />
            2. Recopilar información: Reunir todos los detalles relevantes sobre
            la operación sospechosa, incluyendo nombres, fechas, montos,
            descripción de la actividad, entre otros. <br />
            3. Comunicarse con la UIF: Presentar un reporte de operación
            sospechosa a la UIF a través de su plataforma en línea o por correo
            electrónico, siguiendo las instrucciones y formatos proporcionados
            por la institución. <br />
            4. Mantener la confidencialidad: Es importante mantener la
            confidencialidad de la información relacionada con la operación
            sospechosa y no divulgarla a terceros sin autorización. <br />
            <br />
            Recuerda que reportar operaciones sospechosas es una responsabilidad
            legal y ética para prevenir y combatir actividades financieras
            ilícitas en México.
          </p>
        </ul>
      </div>
      <div class="main-right">
        <h2>Último DOF</h2>
        <div class="dof-summary">
          <p>
            <strong>28/09/2023:</strong> El documento es un aviso sobre la
            modificación de la Guía Interna para la Elaboración y Actualización
            de Manuales Administrativos y/o Documentos Normativos del Instituto
            Nacional de Ciencias Médicas y Nutrición Salvador Zubirán. <br />
            Se informa sobre la actualización de la normativa interna del
            instituto, especificando la fecha de emisión y la materia abordada.
            <br />
            Se ordena la publicación del aviso en el Diario Oficial de la
            Federación. <br />
            <br />
            El aviso fue emitido por el Director General del Instituto, Dr. José
            Sifuentes Osornio, el 28 de septiembre de 2023.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarraNavegacion from '@/components/BarraNavegacion.vue';
import axios from 'axios';

export default {
  name: 'NotificationView',
  data() {
    return {
      showNotifications: false,
      showUserMenu: false,
      menuActive: false,
      welcomeMessage: 'Notificaciones y Actualizaciones',
    };
  },
  components: {
    BarraNavegacion,
  },
  methods: {
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
  mounted() {
    this.checkAuthentication();
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  },
};
</script>

<style>
.clase {
  margin: 0;
  width: 100%;
}

.welcome-text {
  background-color: #c7eef3;
  width: 100%;
  border: 1px solid #000;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
}

.welcome-text .text-container {
  max-width: 100%;
  width: 100%;
  padding: 0 20px 0 130px;
  box-sizing: border-box;
}

.welcome-text h1 {
  padding-top: 20px;
  padding-bottom: 20px;
  margin: 0;
  text-align: left;
  word-break: break-word;
}

.main-content {
  display: flex;
  justify-content: space-between;
  margin: 20px auto;
  max-width: 1500px;
  height: auto;
  padding: 20px;
}

.main-left,
.main-right {
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  box-sizing: border-box;
  border-radius: 8px;
  height: auto;
  overflow: hidden;
}

.main-left {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  flex: 4;
  margin-right: 20px;
  min-height: 400px;
}

.main-right {
  background-color: #fff;
  color: #fff;
  flex: 2;
  background-color: #007bff;
  display: flex;
  flex-direction: column;
  height: auto;
}

h2 {
  margin-top: 0;
  margin-bottom: 0;
}

ul {
  list-style-type: disc;
  padding-left: 20px;
}

.dof-summary {
  color: #fff;
  padding: 10px;
  border-radius: 4px;
  max-height: 200px;
}

.dof-summary p {
  background-color: #fff;
  color: #000;
  padding: 10px;
  border-radius: 4px;
  margin: 0;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
  box-sizing: border-box;
  text-align: justify;
}

.icon {
  color: #555;
  font-size: 35px;
  cursor: pointer;
}

.icon:hover {
  color: #222;
}

@media (max-width: 768px) {
  .navbar-burger {
    display: block;
  }

  .welcome-text {
    text-align: center;
  }

  .welcome-navbar .navbar-menu-1 {
    display: none;
  }

  .navbar-menu {
    display: none;
    padding-top: 0px;
    padding-bottom: 5px;
  }

  .navbar-end {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
  }

  .navbar-menu.is-active {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .navbar-item {
    margin-left: 0;
    margin-bottom: 10px;
    width: 100%;
    text-align: center;
  }

  .navbar-icons {
    margin-left: auto;
  }

  .main-content {
    flex-direction: column;
    padding: 10px;
  }

  .main-left {
    margin-right: 0;
    margin-bottom: 20px;
    height: auto;
  }

  .main-right {
    max-width: 100%;
    height: auto;
  }

  .welcome-text .text-container {
    padding: 0 20px;
  }

  .welcome-text h1 {
    text-align: center;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .navbar-burger {
    display: block;
  }

  .welcome-navbar .navbar-menu-1 {
    display: none;
  }

  .navbar-menu {
    display: none;
  }

  .navbar-menu.is-active {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .navbar-item {
    margin-left: 0;
    margin-bottom: 10px;
    width: 100%;
    text-align: center;
  }

  .navbar-icons {
    margin-left: auto;
  }

  .main-content {
    flex-direction: column;
    padding: 10px;
  }

  .main-left {
    margin-right: 0;
    margin-bottom: 20px;
    height: auto;
  }

  .main-right {
    max-width: 100%;
    height: auto;
  }

  .welcome-text .text-container {
    padding: 0 20px;
  }

  .welcome-text h1 {
    text-align: center;
  }
}
</style>
