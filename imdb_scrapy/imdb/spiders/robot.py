import scrapy

class RobotSpider(scrapy.Spider):
    name = 'robot'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/search/title/?genres=comedy&explore=title_type,genres&ref_=adv_prv']
    _pages = 5
    _current_page = 0
    # Sacar todas las peliculas de https://www.imdb.com/search/title/?genres=comedy&explore=title_type,genres&ref_=adv_prv
    # Incluida la paginacion
    # Sacar tambien informacion:
    '''
    a) el puesto
    b) el título
    c) el director
    d) los actores
    e) el número de reseñas de usuarios y de críticos
    '''
    def parse(self, response):
        base_url = 'https://www.imdb.com'
        movies = response.css('div.lister-list>div.lister-item.mode-advanced')
        for movie in movies:
            url = base_url + movie.css('h3>a::attr(href)').get()
            movie_dic = {
                'index':movie.css('h3>span::text').get(),
                'title':movie.css('h3>a::text').get(),
                'url':url,
                'rating':movie.css('div.ratings-bar>div.inline-block.ratings-imdb-rating::attr(data-value)').get(),
                'created_by':[],
                'actors':[],
                'vote_users':None,
                'vote_critics':None
            }
            yield scrapy.Request(url=url,callback=self.parse_movie,cb_kwargs={'movie_dic': movie_dic})
        # follow next page links
        next_page = response.xpath('//*[@id="main"]/div/div[1]/div[2]').css('a.lister-page-next.next-page::attr(href)').extract()
        if next_page and (self._pages < 0 or self._current_page < self._pages):
            self._current_page += 1
            next_href = next_page[0]
            next_page_url = base_url + next_href
            request = scrapy.Request(url=next_page_url)
            yield request
            
    def parse_movie(self, response,movie_dic):
        directors = response.xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[3]/ul/li[1]/div/ul/li')
        actors = response.xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[3]/ul/li[2]/div/ul/li')
        critics_votes = response.xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/ul/li[2]/a/span').css('span.score::text').get()
        users_votes = response.xpath('//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/ul/li[1]/a/span').css('span.score::text').get()
        
        for director in directors:  
            movie_dic['created_by'].append(director.css('a::text').get())
        for actor in actors:  
            movie_dic['actors'].append(actor.css('a::text').get())
        yield {
                'index':movie_dic['index'],
                'title':movie_dic['title'],
                'url':movie_dic['url'],
                'rating':movie_dic['rating'],
                'created_by':movie_dic['created_by'],
                'actors':movie_dic['actors'],
                'users_votes':users_votes,
                'critics_votes':critics_votes
            }
