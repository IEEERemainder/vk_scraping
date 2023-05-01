from bs4 import BeautifulSoup
import json, os, glob, re

result = []

def safe_get(el, prop):
    if el and el.has_attr(prop):
        return el[prop]
    return ''

def remove_all_but_digits_and_parse_int(x):
    return int(re.sub('\D', '', x) or '-1') # -1 for cases then nothing remains

def process_files_in_dir_by_glob(path, mor):
    pattern = os.path.join(path, mor)
    files = glob.glob(pattern)
    files.insert(0, files.pop()) # move file without number in bracets to the beginning (not tested with timestamps (then more than 100 files downloaded with the same name)), remove if order is unrelevant
    for file in files:
        process_file(file)
    
def process_file(path):
    process_posts(json.load(open(path, encoding='utf-8')))

class SoupWrapper:
    def __init__(self, soup):
        self.soup = soup
    def s(self, selector):
        return SoupWrapper(self.soup and self.soup.select_one(selector) or None)
    def m(self, selector):
        return [SoupWrapper(x) for x in (self.soup.select(selector) if self.soup else [])]
    def g(self, att):
        if self.soup and self.soup.has_attr(att):
            return self.soup[att]
        return ''
    def get_text(self, sep = ''):
    	return self.soup and self.soup.get_text(sep) or ''
    def decompose(self):
    	self.soup and self.soup.decompose()
    def replace_with_children(self):
    	self.soup and self.soup.replace_with_children()

def process_image_data(d):
    for c in ['z', 'y', 'x']: # return best quality
        if c in d:
            return d[c]

def process_dup_comments(data):
    if len(data) == 0: return
    last = data[-1]
    comments = last["first_comments"]
    d = []
    lastAdded = None
    for comment in comments:
        if comment != lastAdded:
            d.append(comment)
            lastAdded = comment
    last["first_comments"] = d

def process_posts(posts):
    for post in posts:
        soup = BeautifulSoup(post, "html.parser")
        sw = SoupWrapper(soup)
        comment_author = sw.s('.author')
        is_comment = comment_author.soup != None
        is_post = not is_comment
        if is_post:
            process_dup_comments(result)
            id_ = sw.s('a.PostHeaderTitle__authorLink').g('data-post-id')
            text_el = sw.s('.wall_post_text')
            show_more = text_el.s('.PostTextMore')
            show_more.decompose() # clear 'Показать еще'
            hidden_part_span = text_el.s('span')
            hidden_part_span.replace_with_children() # clear odd \n
            text = text_el.get_text('\n')
            subtitle_from = sw.s('a.PostHeaderSubtitle__item').g('href')
            when = sw.s('time').get_text()
            imgs_data = [process_image_data(json.loads(x.g('data-options'))['temp']) for x in sw.m('[data-options]')]
            audios_data = [json.loads(x.g('data-audio')) for x in sw.m('[data-audio]')]
            lincs = [x.g('href') for x in sw.m('a')]
            away_lincs = [x for x in lincs if x.startswith('/away.php')]
            videos_lincs = [x for x in lincs if x.startswith('/video') and x[6] in '-0123456789'] # is 7'th symbol always present?
            other_lincs = [x.g('href') for x in sw.s('.wall_text').m('a')]
            other_lincs = [x for x in other_lincs if not x.startswith('/feed?section=search&amp;q=%23') and x not in other_lincs and x not in videoLincs] # remove search tags and lincs from other cats
            votingEl = sw.s('.media_voting')
            votingData = {}
            if votingEl.soup:
                question = votingEl.s(".media_voting_question").get_text();
                info = votingEl.s(".media_voting_info").get_text();
                options = [x.get_text() for x in votingEl.m(".media_voting_option_text")]
                votersCount = remove_all_but_digits_and_parse_int(votingEl.s("._media_voting_footer_voted_text").get_text());
                firstVoters = [x.g('href') for x in votingEl.m(".media_voting_footer_voted_friend")]
                votingData = {"question" : question, "info" : info, "options" : options, "voters_count" : votersCount, "first_voters" : firstVoters}    
            stats = [remove_all_but_digits_and_parse_int(x.get_text()) for x in sw.m('.PostBottomAction__count')]
            if stats != []:
                lices = stats[0]
                comments = stats[1] if len(stats) == 3 else 0 # may miss comments and reposts? TODO
                reposts = stats[2] if len(stats) == 3 else (stats[1] if len(stats) == 2 else 0) # reposts can be banned?
            else:
                lices = comments = reposts = -1
            resultPost = {'id' : id_, "from" : subtitle_from, "text" : text, 'when' : when, 'imgs' : imgs_data, 'videos' : videos_lincs, 'audios' : audios_data, 'lincs' : {'away' : away_lincs, 'other' : other_lincs}, 'first_comments' : [], "voting_data" : votingData, 'stats' : {'lices' : lices, 'comments' : comments, 'reposts' : reposts}}
            result.append(resultPost)
        elif is_comment:
            author_el = sw.s('.author')
            from_ = author_el.get_text()
            from_id = author_el.g('data-from-id')
            text = sw.s('.wall_reply_text').get_text('\n') # no support for everything except text for now; remove \n after mention? TODO
            when = sw.s('.rel_date').get_text()
            #print("before", result[-1]["comments"])
            result[-1]['first_comments'].append({'from' : from_, 'from_id' : from_id, 'text' : text, 'when' : when})
            #print("after", result[-1]["comments"])
path = '/media/paul/B0701CFA701CC94C/Users/Paul/Downloads/'
mor = 'psyamour_part*.json'
# process_files_in_dir_by_glob(path, mor)
process_file('/home/paul/Загрузки/netstalcing.json')
