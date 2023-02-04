from lib.GlobalImport import requests

class RiotApi(object):
    def __init__(self, api_key: str, region: str):
        self.__RIOT_API_KEY = api_key
        self.__HEADER = {'X-Riot-Token': self.__RIOT_API_KEY}
        
        self.__REGION = 'tw2'
        if region == 'na':
            self.__REGION = 'na1'
        elif region == 'eu':
            self.__REGION = 'euw1'
            
        self.__ROUTING = 'sea'
        if region == 'na':
            self.__ROUTING = 'americas'
        elif region == 'eu':
            self.__ROUTING = 'europe'
            
        self.__BASE_URL = ".api.riotgames.com/lol/"
        self.__API_URL_SUMMONER_V4 = "https://" + self.__REGION + self.__BASE_URL + "summoner/v4/summoners/"
        self.__API_URL_MATCH_V5 = "https://" + self.__ROUTING + self.__BASE_URL + "match/v5/matches/by-puuid/"
        self.__API_URL_MATCH_V5_MATCHID = "https://" + self.__ROUTING + self.__BASE_URL + "match/v5/matches/"

    def get_summoner_by_name(self, summoner_name: str) -> dict:
        """Summoner Infos and Ids
        @param summoner_name: LoL summoner name
        @return json object of infos and ids
        """
        url = self.__API_URL_SUMMONER_V4 + "by-name/" + summoner_name
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    def get_matches_by_name(self, puuid: str) -> dict:
        """Get summoner match history by name"""

        url = self.__API_URL_MATCH_V5 + puuid + "/ids"
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    def get_matches_by_matchid(self, matchid: str) -> dict:
        """Get matches by match id"""

        url = self.__API_URL_MATCH_V5_MATCHID + matchid
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    def get_summoner_by_puuid(self, puuid: str) -> dict:
        """Get summoner info by puuid"""

        url = self.__API_URL_SUMMONER_V4 + "by-puuid/" + puuid
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    #call
    def get_latest_matches_by_name(self, summoner_name:str) -> dict:
        """Latest match history info by summoner name"""

        gsbn = self.get_summoner_by_name(summoner_name)

        if gsbn is not None and int(len(gsbn)) > 0 and 'puuid' in str(gsbn):
            gsbn = gsbn['puuid']

            gmbn = self.get_matches_by_name(gsbn)

            if gmbn is not None:
                # attempt retry once if 503 service unavailable
                if 'status' in gmbn and str(gmbn['status']['status_code']) == '503':
                    gmbn = self.get_matches_by_name(gsbn)

                if 'status' not in gmbn and int(len(gmbn)) > 0:
                    gmbn = gmbn[0]
                    matchDetails = self.get_matches_by_matchid(gmbn)
                    
                    if matchDetails is not None:
                        if 'status' in matchDetails and str(matchDetails['status']['status_code']) == '503':
                            matchDetails = self.get_matches_by_matchid(gmbn)

                        if 'status' not in matchDetails and int(len(matchDetails)) > 0:
                            return matchDetails
        return None