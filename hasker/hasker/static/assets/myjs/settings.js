let app = new Vue({
  el: "#settings",
  delimiters: ["{", "}"],
  data: {
    login: null,
    foto: null,
    file: null,
    email: null,
    request: false,
    visible: true,
    settings: {},
    styleObject: {
      width: '118px',
      height: '118px',
      background: this.foto,
    },
  },

  methods: {
    init: function() {
        this.get_settings();
    },
    get_settings: function() {
      axios.post("get_settings/", {
        'Accept': 'application/json'
        
      }).then(async response => {
        const data = await response.data;
        all_data = JSON.parse(data)
        console.log(all_data)
        this.login = all_data['login']
        this.email = all_data['email']
        this.foto = all_data['foto']
      });
    },

    submitFile(){
            let formData = new FormData();
            formData.append('file', this.file);
            formData.append('login', this.login);
            formData.append('email', this.email);
            console.log(this.file)
            axios.post( 'change_user_data/',
                formData
            ).then(function(){
          console.log('SUCCESS!!');
          app1.get_user_data()
        })
    },
    hide_foto(){
      this.visible = false
      this.file = this.$refs.file.files[0];
    },
      

  },
  mounted: function () {
  this.init();
  }
    
})