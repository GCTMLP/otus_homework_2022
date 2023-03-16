let app = new Vue({
  el: "#answers",
  delimiters: ["{", "}"],
  data: {
    answer_num:0,
    num: null,
    request: false,
    answers: {},
    make_truth: null,
    question: [],
    popular_questions: {},
    a_text: null,
    filter: {
      page: 1,
      limit: 5,
      pages_big: 0,
      search: '',
    },
    new_quest: {
      title: null,
      text: null,
      tags: null,
    }
  },
  methods: {
    init: function() {
        url = window.location.href
        re = /q=(\d+)/
        this.num = url.match(re)[1];
        this.get_answers(this.num, this.filter.page)
        this.get_popular_questions()

    },
    get_answers: function(num, page) {
      const params = {
        q_num : num,
        page: page,
        limit: this.filter.limit,
        search: this.filter.search
      };
      axios.post("get_all_answers/", params, {
        'Accept': 'application/json'
        
      }).then(async response => {
        const data = await response.data;
        all_data = JSON.parse(data)
        
        this.answers = all_data['data']
        this.question = all_data['question'][0]
        this.make_truth = all_data['make_true_answer']
        console.log(this.make_truth)
        q_count = Number(all_data['count'])
        console.log(q_count)
        this.filter.pages = Math.floor(q_count / this.filter.limit);
        if(q_count % this.filter.limit != 0){
          this.filter.pages += 1

        }
      });
    },

    get_popular_questions: function(page) {
      
      axios.post("/get_popular_questions/",{
        'Accept': 'application/json'
        
      }).then(async response => {
        const data = await response.data;
        all_data = JSON.parse(data)
        console.log(all_data)
        this.popular_questions = all_data
      });
    },
    minus_page: function(){
      if (this.filter.page % 5 == 0 && this.filter.pages_big+1 == this.filter.page){
        this.filter.pages_big-=4
        this.filter.page = this.filter.page-=1
      }
      else{
        this.filter.page = this.filter.page-=1
      }
      if(this.filter.page % 5 == 0 ){
        this.filter.pages_big-=4
      }
      this.init()
    },

    plus_page: function(){
      if (this.filter.page % 5 == 0 && this.filter.pages_big+5 == this.filter.page){
        this.filter.pages_big+=4
        this.filter.page = this.filter.page+=1
      }
      else{
        this.filter.page = this.filter.page+=1
      }
      if(this.filter.page % 5 == 0){
        this.filter.pages_big+=4
      }
      this.init()
    },

    change_page_big: function(page_chosen){
      if(page_chosen % 5 == 0 && page_chosen > this.filter.page){
        this.filter.pages_big+=4
        console.log(this.filter.pages_big)
      }
      if(page_chosen % 5 == 0 && page_chosen < this.filter.page){
        this.filter.pages_big-=4
        console.log(this.filter.pages_big)
      }
      console.log(this.filter.pages_big)
      this.filter.page = page_chosen
      this.init()
    },
    change_count: function(limit){
      this.filter.limit = limit
      this.filter.page = 1
      this.init()
    },
    clean_search: function(){
      this.filter.search = null
      this.init()
    },
    answer_question: function(){
      console.log()
      
      params = {
        text: this.a_text,
        q_id: this.num,
      }
      axios.post("answer_question/", params, {
        'Accept': 'application/json'
          
      }).then(async response => {
        const data = await response.data;
        console.log(JSON.parse(data))
        
        this.init()
        this.a_text = null  
      });
      
      
    },

    plus_vote: function(id){
      params={
        id: id
      }
      axios.post("plus_vote/", params, {
        'Accept': 'application/json'
          
      }).then(async response => {
        this.init()       
      });
    },
    minus_vote: function(id){
      params={
        id: id
      }
      axios.post("minus_vote/", params, {
        'Accept': 'application/json'
          
      }).then(async response => {
        this.init()       
      });
    },

    uncorrect: function(id_answer){
      console.log(id_answer)
      params={
        id_a: id_answer,
        func: "uncorrect"
      }
      axios.post("correct_uncorrect/", params, {
        'Accept': 'application/json'
          
      }).then(async response => {
        const data = await response.data;
        this.init() 
      });
    },

    correct: function(id_answer, id_question){
      console.log(id_answer)
      params={
        id_a: id_answer,
        id_q: id_question,
        func: "correct"
      }
      axios.post("correct_uncorrect/", params, {
        'Accept': 'application/json'
          
      }).then(async response => {
        const data = await response.data;
        this.init() 
      });
    }

  },
  mounted: function () {
  this.init();
  }
})