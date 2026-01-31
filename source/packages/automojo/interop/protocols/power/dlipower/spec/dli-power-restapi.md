# DLI Power REST API Spec (Markdown)

_Converted from the provided PDF: `dli-power-restapi.pdf`._

---

DLI REST-style API Reference
GeneratedbyDoxygen
20221009T204818Z

ii
1Overview 1
1.1Targetaudience . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
1.2Designgoals. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
2RESTarchitecturalstyleintroduction 2
2.1HTTPverbs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
2.2HTTPrequestheaders . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.3Contenttypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
3Basicexamples 4
4Datamodel 7
4.1Scalartypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
4.2Singletontypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
4.3Containertypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
4.4Thesumtype . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
4.5Thecalltype . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
4.6Constraints . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
5Supportedstandardinterfaces 10
5.1URIs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
5.2HTTPverbs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
5.3HTTPauthentication. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
5.4InputMIMEtypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
5.4.1application/json . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
5.4.2text/plain . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
5.4.3application/x-www-form-urlencoded . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
5.5PatchMIMEtypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
5.5.1application/json-patch+json . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
5.5.2application/x-www-form-urlencoded . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
5.6OutputMIMEtypes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
5.6.1application/json . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
5.6.2text/html . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
5.6.3text/plain . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
5.7Preferenceindication . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
6Extensionstothestandardinterfaces 14
6.1Cross-siterequestforgeryprotection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
6.2HTTPverbtunneling. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
6.3MatrixURIsandworkingwithmultipleresourcesinparallel . . . . . . . . . . . . . . . . . . . . . . 15
6.4Linkrelation'templated' . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
6.5Responsedepthlimiting . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
7Deviationsfromstandardsandcommonpractices 17
DLIREST-styleAPIReference:20221009T204818Z

1Overview 1
7.1Nonstandard207Multipleresponsesformat . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
7.2PUTandDELETEmethodsnotalwaysidempotent . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
7.3Semanticallyside-effect-freecallsstillneedPOST . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
7.4PATCHisallowedonread-onlyresources . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
7.5SomePATCHoperations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
7.6Templatedand'hackable'URIs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
Bibliography 20
# 1 Overview
REST is an architectural style where data are presented and manipulated as an hierarchy of resources, and the
underlying communications protocol (commonly HTTP) is used to perform action signaling, content negotiation,
etc [11]. In practice this means automated clients for it are easier to implement; they can send and receive state
in different formats (representations of resources). The REST-style API follows the principles of REST principles
wherepossiblewithoutsacrificingsimplicityoraddingunnecessarybloat.
## 1.1 Targetaudience
TheREST-styleAPIisdesignedtobeusedforautomatingaccesstothedevice,butcanalsobeusedmanuallywith
thebrowser. Duetothewaydeviceconfigurationisimplemented,anynewconfigurationvariablesareexposedto
theRESTAPIautomatically,whiledesigningwouldtaketime.
## 1.2 Designgoals
• Simpleuniformwidely-implementedinterfaces
TheREST-styleAPIidentifiesresourceswithURIs[2]. Justabouteverythingthereistoknowaboutthecontroller(statesoftheoutletsandtheirnames,differentenvironmentmeters,AutoPingitems,networkinterfaces
andauthorizedusers,etc.)hasitsplaceinanhierarchicalURInamespace.Groupsofsimilarresources(e.←(cid:45)
g. all locked outlets, or all voltage meters, or all enabled AutoPing items) have matrix URIs (see later) to
referencethemasagroup.
TheAPIreliesonHTTP,awidelyimplementedprotocol,toperform:
– actionsignaling(whattodowiththespecifiedresource);
– contentnegotiation(whatformatyouwanttoinputdatainandhowyouwanttoreceiveoutput);
– limitingoutputverbosityornesting(onlygetthedatayouneed);
– relatedresourcediscovery(withtheLinkheaders).
• FeaturecompatibilitywithexistingwebUIandlegacyAPI
Ifyouarereadingthis, youhaveprobablyusedsomescriptstoaccesstheDLIpowercontrollers. Itwasn't
convenient,sometimesinvolvedreverseengineeringthewebpagesoutputbythedevices,etc. Butitallowed
youtoautomatealotofdeviceconfigurationandcontroltasks. TheREST-styleAPIintendstoallowaccess
tothesame,andmoreparameters,inauniformfashion.ThelegacyAPIswillremaininplace,butnowthere's
analternative.
DLIREST-styleAPIReference:20221009T204818Z

• Discoverability
YoucanuseyourwebbrowsertoaccesstheAPI,todiscoverthevisibleconfigurationandstateresources,
andmanipulatethem. That'sactuallywhatthewebUIadvisesyoutodo.
Discovering the API without a browser is also possible, just less convenient. For example, you can get a
representation of the whole configuration by issuing a GET request to the API root (/restapi/) requesting
output as JSON (Accept: application/json). However, without extra information it's not obvious what further
actionsyoucantake,andHTMLoutputexplainsmostofittoyou(andprovidesformsforyou).
• Extensibility
ThewaytheAPIisdesignedmakesiteasierforustointegratenewfeaturesintothecontrollers,andforyouto
findthem.Forexample,ifyouhaveascripttocyclealloutlets,itwillreallycyclethemall,evenifthecontroller
hasmoreoutletsthanyouexpected.
• Easeofuseforcommonoperations
TheunderlyingdatamodelandprimaryinterchangeformatarebasedonJSON,acompactwidelysupported
notation[3]. Forexample,youcanswitchoffallnon-lockedoutlets,orretrievethestatesofalloutletsatonce,
withasinglerequest(inthelattercaseyouwilljustreceiveanarrayofstatesifyouneed,youwon'thaveto
parseHTML),andthatwithoutsacrificingtheuniformity.
• Flexibility
RequestswithdifferentHTTPheaderswillmayacceptdifferentargumenttypesandyielddifferentrepresentationsofresources(e.g. plaintext,HTML,JSON,etc.). Ifyouareinterestedinayetunsupportedencoding,
pleaseletusknowandwe'llhappilyaddit,withoutsacrificingcompatibility.
• Consistency
Differentmeansofachievingseeminglysameresultsshouldbeasequivalentaspossible. Forexample,you
couldchangeapropertyofanobjectbyissuingaPUTrequesttothatproperty,orbyissuinganappropriate
PATCHrequesttoparent(object's)URL,andthebehaviorshouldbethesame;samegoesforDELETE.
# 2 REST architectural style introduction
RESTexposesthemanipulatedobjectsasanhierarchicalcollectionofresources. Youmaythinkofsuchcollection
asofadirectoryinafilesystem, anSNMPOIDsubtree, etc. Resourcescanberetrieved, modified, createdand
deleted; all of these operations are performed using standard HTTP methods, with well-defined semantics and
behavioradjustablebystandardHTTPheaders.
## 2.1 HTTPverbs
IntheRESTarchitecturalstyle,HTTPverbsareusedtoindicatewhatyouwanttodowiththeresource.
ThefollowingHTTPverbsaresupported:
• GET
GETisusedtoretrieverepresentationoftheresource.
• HEAD
HEADissimilartoGET,butreturnsonlytheheadersfortheresource.
• POST
POSTisusedtocreateanewelementinthecollectionresource,orperformthefunctioncall.
• PUT
PUTisusedtocreateoroverwritetheresource.
DLIREST-styleAPIReference:20221009T204818Z

## 2.2 HTTPrequestheaders 3
• PATCH
PATCHisusedtoupdatetheresourceinplace,possiblyconditionally.
• DELETE
DELETEisusedtodeletetheresourcefromitscollection.
• OPTIONS
OPTIONSisusedtopreflightcross-originrequests(it'susuallysentinternallybybrowsers).
## 2.2 HTTPrequestheaders
Request headers inform the server about what and how the client wants the server to return. Here are the more
importantones:
• Authorization
Authorizationcontainsaccesscredentials;it'susuallysentinternallybyclients.
• Accept
Acceptindicatesclient'spreferencesinthecontenttypeofrepresentationtobereturnedbytheserver.
• Content-Type,Content-Length
Content-TypeandContent-Lengthintherequestindicatethekindandsizeofpayloadtheclientsendstothe
server.
• Range
Rangeallowstoselectonlyaportionoftheresourcetoberetrieved. Wedefineaspecifickindofrangethat
limitstreenesting.
• Prefer
Preferallowstocustomizedifferentaspectsofserverbehaviour,e.g. whetherthefullrepresentationoftheresource
shouldbereturned,etc.
• X-Requested-With
AnX-Requested-With: XMLHttpRequestheaderindicatesthatXMLHttpRequesthasbeenusedtoissuethe
request(it'susedforcross-siterequestforgeryprevention).
Additionally,thefollowingnonstandardheadersaresupported:
• X-HTTP-Method
X-HTTP-MethodcanbeusedtoemulateaPUT/DELETE/PATCHrequestiftheclientdoesn'tsupportit(itis
honoredinPOSTrequestsonly).
• X-CSRF
An X-CSRF header with any value can be used to mark legitimate requests (used for cross-site request
forgeryprevention).
DLIREST-styleAPIReference:20221009T204818Z

## 2.3 Contenttypes
# 3 Basic examples
TheseexamplesdonotintendtodescribetheAPIcompletely;rather,theyshowthewaysinwhichitcanbeused
to encourage further reading. They use 'curl', a popular HTTP command-line client, and assume you have a unit
accessibleat
http://admin:1234@192.168.0.100/
Commandsandresponsesareformattedandsometimestruncatedforreadability.
• Retrievealltop-levelresourcesintheRESTAPI:
curl -H "Range: dli-depth=1" -H "Accept: application/json" \
--digest ’http://admin:1234@192.168.0.100/restapi/’
Result:
# 200 OK
{
"relay": {"$ref":"relay\/", "title":"Relay object"},
"auth": {"$ref":"auth\/", "title":"Authentication server object"},
"config": {"$ref":"config\/", "title":"Configuration server object"},
"network": {"$ref":"network\/", "title":"Network configuration data"},
"autoping": {"$ref":"autoping\/", "title":"Autoping server object"},
"script": {"$ref":"script\/", "title":"Scripting server object"},
"meter": {"$ref":"meter\/", "title":"Meter server object"},
"renderer": {"$ref":"renderer\/", "title":"Renderer object"}
}
• Retrievetwolevelsofgenericconfiguration-relatedresourcesintheRESTAPIinfreeformtext:
curl -H "Range: dli-depth=2" -H "Accept: text/plain" \
--digest ’http://admin:1234@192.168.0.100/restapi/config/’
Result:
# 200 OK
object:
allow_plaintext_logins = false
protect_private_config = false
hide_wifi_key = false
custom_brand_url = false
syslog_ip_address = 192.168.0.1
protect_firmware = false
is_registered = false
hide_passwords = true
protect_network = false
custom_brand_name = false
known_quantities = illuminance=(...Quantity...), current=(...Quantity...), [truncated]
allow_jsonrpc = false
https_port = 443
custom_brand_logo_height = false
refresh_enabled = true
protect_maintenance = true
custom_brand_logo_width = false
http_port = 80
known_timezones = UTC-6=(...Timezone...), UTC+4=(...Timezone...), [truncated]
protect_admin = false
allow_restapi = true
relax_nonhtml_content_types = false
lockout_delay = 60
DLIREST-styleAPIReference:20221009T204818Z

3Basicexamples 5
plots = (...Plot...),(...Plot...), [truncated]
ssh_enabled = true
timezone = UTC
ssh_port = 22
upgrade_notify_beep = false
meters = (...Meter configuration...),(...Meter configuration...), [truncated]
custom_brand_company_name = false
refresh_delay_minutes = 1
links = (...Link...)
version = (...Version...)
hardware_id = (...)
custom_brand_logo = false
image_format = svg
hostname = (...Hostname...)
serial = (...Serial...)
relax_nonhtml_methods = false
upgrade_notify_blink = false
• Switchalloutletsoff:
curl -v -X PUT -H ’X-CSRF: x’ -H "Accept: application/json" --data ’value=false’ --digest
’http://admin:1234@192.168.0.100/restapi/relay/outlets/all;/state/’
Result:
# 207 Responses from multiple resources follow
• AddalinktothewebUI:
curl -H ’X-CSRF: x’ --data ’href=http://www.digital-loggers.com/&description=Digital+Loggers’ \
--digest ’http://admin:1234@192.168.0.100/restapi/config/links/’
Result:
# 201 created
• Getstatesofoutlets#1,#2and#5inasingleJSONarray:
curl -H "Accept: application/json" --digest \
’http://admin:1234@192.168.0.100/restapi/relay/outlets/=0,1,4/state/’
Result: 207Responsesfrommultipleresourcesfollow
[true,true,true]
• GetnamesandphysicalstatesofalllockedoutletsinasingleJSONarray:
curl -H "Accept: application/json" --digest \
’http://admin:1234@192.168.0.100/restapi/relay/outlets/all;locked=true/=name,physical_state/’
Result: 207Responsesfrommultipleresourcesfollow
["a9999",true,"Outlet 4",false]
• Add a user, and also return the representation for the user object (when showing non-administrative user
passwordsisenabled):
curl -H "Accept: application/json" -H ’Prefer: return=representation’ -H ’X-CSRF: x’ \
--data
’name=fred&password=foobar&is_allowed=true&outlet_access=false,false,false,false,false,false,false,false’
--digest \
’http://admin:1234@192.168.0.100/restapi/auth/users/’
Result:
# 201 Created
DLIREST-styleAPIReference:20221009T204818Z

```json
{
"name":"fred",
"password":"foobar",
"is_allowed":true,
"is_admin":false,
"outlet_access":[false,false,false,false,false,false,false,false]
}
• Gettheindicesofallowedusers:
curl -H "Accept: application/json" --digest
’http://admin:1234@192.168.0.100/restapi/auth/users/is_allowed=true/=/’
Result:
# 207 Responses from multiple resources follow
[0,1,2]
• Gettheindexoftheadminuser(expectingexactlyoneadmin):
curl -H "Accept: application/json" --digest
’http://admin:1234@192.168.0.100/restapi/auth/users/one;is_admin=true/one;=/’
Result:
# 200 OK
• GetunitfirmwareversionandserialnumberinasingleJSONarray:
curl -H "Accept: application/json" --digest \
’http://admin:1234@192.168.0.100/restapi/config/=version,serial/’
Result:
# 207 Responses from multiple resources follow
["(...Version...)","(...Serial...)"]
• GetindicesandnamesforallmetersinasingleJSONarray:
curl -H "Accept: application/json" --digest \
’http://admin:1234@192.168.0.100/restapi/meter/values/all;/=,name/’
Result:
# 207 Responses from multiple resources follow
[
"bus.0.current","current",
"bus.0.voltage","voltage",
"bus.0.total_energy","total energy",
]
• GetnamesandvaluesforallbusBmetersinasingleJSONarray:
curl -H "Accept: application/json" --digest \
’http://admin:1234@192.168.0.100/restapi/meter/values/all;bus=1/=name,value/’
Result:
# 207 Responses from multiple resources follow
DLIREST-styleAPIReference:20221009T204818Z

```

4Datamodel 7
[
"current",0,
"voltage",167,
"total energy",645501.064831
]
• Change the administrator password, and return the administrator configuration (the administrator password
isnevershown):
curl -H "Accept: application/json" -H ’Prefer: return=representation’ -H ’X-CSRF: x’ \
-X PATCH --data ’old_password=1234&new_password=4321’ --digest \
’http://admin:1234@192.168.0.100/restapi/auth/users/is_admin=true/’
Result:
# 200 OK
{
"name":"admin",
"password":{"$ref":"password/","title":"Password"},
"is_allowed":true,
"is_admin":true,
"outlet_access":[true,true,true,true,true,true,true,true]
}
• Runscriptingfunction'test'withoutarguments:
curl -H ’X-CSRF: x’ -H "Content-Type: application/json" -H "Accept: application/json" --digest \
--data-binary ’[{"user_function":"test"}]’ ’http://admin:1234@192.168.0.100/restapi/script/start/’
Result(returnsthreadidentifier,whichisaJSONstring):
# 200 OK
"11"
• Runscriptingfunction'test'witharguments1.5and"hello":
curl -H ’X-CSRF: x’ -H "Content-Type: application/json" -H "Accept: application/json" --digest \
--data-binary ’[{"user_function":"test","source":"test(1.5,\"hello\")"}]’ \
’http://admin:1234@192.168.0.100/restapi/script/start/’
Result(returnsthreadidentifier,whichisaJSONstring):
# 200 OK
"12"
• ObtaintheIPaddressoftheclientsendingtherequestasseenbythecontroller:
curl -H "Accept: application/json" --digest \
’http://admin:1234@192.168.0.100/restapi/cred/ip_address/’
Result:
# 200 OK
"192.168.0.2"
# 4 Data model
ThedatamodelisbasedontheJSONdataformat,andborrowsmosttypedefinitionsfromthere. Wewillstartwith
thetypespresentinJSON.
DLIREST-styleAPIReference:20221009T204818Z

## 4.1 Scalartypes
Scalardatatypes(havingnointernalstructureandcorrespondingtosimpleproperties)are:
• astringliteral;
• anumberliteral(followingJSONrules,itmustbeafinitenumber,sonoinfinitiesorNaNs).
## 4.2 Singletontypes
Singletondatatypesareaspecialtypeofscalartypes. Theyarealsoknownasunittypes, andtheyhaveonlya
singlevalue:
• theconstantvaluetrue;
• theconstantvaluefalse;
• theconstantvaluenull.
Youmaywonderwhythere'snoseparatebooleantype.Surprisingly,theJSONspecificationdoesn'tmentionit.true
andfalsearejustseparatespecialvalues,likenull. Seebelowforhowthebooleantypeishandled.
## 4.3 Containertypes
JSONdefinestwocontainertypes:
• arraysareorderedlistswithintegerkeyslike:
[1,"a",true]
• objectsareunorderedmapswithstringkeyslike:
{"name":"fred","is_admin":true}
Inourdatamodel,acontainercaneitherhaveanarbitrarynumberofkeys,allwiththesametype(calledtheelement
type,andwewillcallsuchcontainershomogeneous),orasetofpre-specifiedkeys(whichwewillcallfields),each
withitsowntype(whichwewillcallheterogeneous). So, wedistinguishthefollowingfourtypes, whicharebased
ontheJSONonesbutadditionallyconstraintheirvalues:
container object-based array-based
heterogeneous object tuple
homogeneous map array
Themostimportantdifferenceisthatyoucanonlyaddorremoveelementsfromhomogeneouscontainers(maps
andarrays).
Additionally,allJSONobject-basedvalueshaveanadditionalimplicitconstraintonthekeys: theycannotbeempty.
Forexample,
{"":"I am empty!"}
DLIREST-styleAPIReference:20221009T204818Z

## 4.4 Thesumtype 9
is a valid JSON object, but is guaranteed to neither be accepted nor generated by the API. Among other things,
such fields would have syntactically invalid URIs (with a double slash). This constraint also allows us to give the
emptystring""aspecialmeaningwhenitappearsintheplaceofanobjectkeyname.
Therearealsotwomoretypesofresources,whichdon'tcorrespondtoJSONtypes.
## 4.4 Thesumtype
ThesumtypeissomethingthatcannotbeattributedtoaJSONvalue,it'satypeoftheresource. Aresourceofa
sumtypecanhaveanyvalueofaspecifiedsetoftypes(ifyouarefamiliarwitha'restrictedvariant'type,ora'union'
type,thisissimilar). Forexample,abooleanisthesumtypeofconstanttrueandconstantfalse. An'optional'string
(string that can be said to have no value at all) can be encoded as the sum type of the string type and constant
null(orconstantfalseinsomecases). Withadditionalconstraints(seebelow),thesumtypecanbeusedtomodel
enumerationsfromafixedlistofvalues.
Thetypeisnota'taggedvariant',thatis,itdoesn'tstoretheinformationaboutwhichvariantisstored,itonlystores
thedata.
Thesumtypehasthefollowingadditionalrestrictions:
• Asumtypecannotbeavariantofanothersumtype(thatwouldberedundantandaddunneededcomplexity).
• Thevariantcorrespondingtoacontainedvaluemustbeuniquelydeterminedbythevalueitself(notagging);
• Asumtypecanonlyhaveatmostonecontainervariant;thisispartlyaconsequenceofthepreviousrestriction,otherwiseanemptymapandanemptyobjectwouldbeindistinguishable.
## 4.5 Thecalltype
Thecalltypeisatypeofafunctioncall. IthasnovaluethatcanberepresentedinJSON,buthasargumentand
resulttypes. Theargumenttypeisusuallyatuplecontainingthefunction'sarguments. Resourceswiththistypeare
accessedusingPOST,wheretherequestcontentspecifiesthearguments,andreturnavalueoftheresulttype.
ThecalltypemaybeseenasaviolationoftheRESTprinciples,butinpracticesomeactions(likecyclinganoutlet)
aremorenaturallymodeledwithafunctioncallthanwitharesource.
The call type cannot by a variant of a sum type; resources with this type are usually contained in object-type
resources,whichmodelstraditionalobjectmethodcalls.
## 4.6 Constraints
Anynon-calldatatypecanhaveadditionalconstraintsonit. Inputdatawhichdon'tsatisfyconstraintsarerejected.
Forexample,anumbercanberestrictedtovaluesgreaterthanzero,orastringcanberestrictedtobeequalto"".
Another common constraint is that one value (usually a scalar value) is an index into another value (usually of a
containertype). Thiscanbeseenasanalternativeforasumtypeformodelingenumerations,butinthiscase,the
enumeration is 'open': the reference side doesn't enumerate what values exactly are; the referee does. This can
alsobeseenasa'foreignkey'relationbypeoplewitharelationalbackground.
For example, in miscellaneous configuration there is a tunable string value that represents the preferred image
formatforplotsandmetersinthewebUI.Itislocatedat
DLIREST-styleAPIReference:20221009T204818Z

/restapi/config/image_format/
andhastheconstraintthatisanindexinto
/restapi/renderer/known_image_formats/
Ifyougothere,youwillseeamap
gif => GIF
jpeg => JPEG
png => PNG
svg => SVG
that represents the image formats supported by the renderer. If you attempt to PUT any other value into
/restapi/config/image_format/,youwillreceivea409Conflictresponse.
# 5 Supported standard interfaces
## 5.1 URIs
IntheRESTarchitecturalstyle,URIsareusedtoindicatewhatobject(resource)youwanttoaccess.
All API URIs must end with a slash ('/'). This is not some hard limitation, but other URIs are reserved for future
extension. Atthemoment,ifyouattemptarequesttoanon-slash-terminatedURI,youwillreceiveanappropriate
30xredirecttothecorrect(slash-terminated)URI.Correctlyconfiguredclients(e.g.browsers)willfollowtheredirect.
Youshouldn'trelyonthisbehaviorthough.
EachlevelofobjectmodelhierarchythatneedstobetraversedcorrespondstoaURIcomponent. Asisstandard
procedure,allcharactersexceptalphanumerics('A'..'Z','a'..'z','0'..'9'),dashes('-'),underscores('_'),dots('.') and
tildes ('∼') must be percent-encoded in URI components. Additionally, as a non-standard extension, URI componentscorrespondingtohierarchylevelsexactlyequaltoasingledot('.') ortwodots('..') mustbeprecededbyan
exclamationmark(translatedto'!.' or'!..',respectively)toavoidbeingeliminatedbythedotsegmentremovalprocedure(see[2]). Asliteralexclamationmarksarereservedandmustbepercent-encoded,thiscreatesnoambiguity.
Theexclamationmarkisotherwisereservedandshouldnotbeusednon-escapedinanyothercase.
URI query parameters (like ?a=b&c=d ...) are not currently used, and reserved for future extension. It should be
notedthatsomebrowsersthatstillsurvivedespiteallreason(IE6)haveproblemswithqueryparametersanddigest
authentication(seebelow).
Instead of query parameters, URI matrix parameters, a less-widespread feature, is used. They enable parallel
operationsonsimilarresources,andarediscussedbelow.Fornow,itsufficestosaythatyoushouldmakesurethat
ifyousendcharacters';','='or','inaURIpathsegment,youshouldpercent-encodethemunlessyouknowwhat
youaredoing.
## 5.2 HTTPverbs
AllverbsdescribedinHTTPverbsaresupported,withsomeDeviationsfromstandardsandcommonpracticesdeviationsfromstandardsemantics.
DLIREST-styleAPIReference:20221009T204818Z

## 5.3 HTTPauthentication 11
## 5.3 HTTPauthentication
In the REST architectural style, standard authentication methods are preferred. This includes Basic and Digest
authentication.
BecauseBasicauthsendstheusernameandpasswordinplaintext,itisdisabledinnewerDLIcontrollersunless
"Allowlegacyplaintextloginmethods"(/restapi/config/allow_plaintext_logins/)isset.
Digestauthisachallenge-responsemechanismwhichissimilartothelegacyauthenticationmethodinwhichthe
clientreceivedachallengefromtheserverandhasheditcombinedwiththeusernameandpasswordtoprovetheir
identity, but has additional security features, as well as the benefits of being standard and widely implemented.
Digest auth supports different "quality of protection" (qop) levels. qop="auth" and qop="auth-int" are supported.
SeetherelatedRFCS[8],[7]fordetails.
Ifyouarereallysecurity-conscious,youshoulddisableHTTPcompletelyinthecontroller'swebUI,anduseHTTPS
only, as this will provide a higher degree of security and make Basic and Digest authentication methods more or
lessequivalent.
## 5.4 InputMIMEtypes
Data in the following formats can be specified as a representation of a resource (for PUT or POST) using the
Content-Typeheader:
### 5.4.1 application/json
JSONisthemaininterchangeformat. Itisacceptedbyallresourcesinallcircumstances. Othercontenttypescan
bethoughtofasiftheywerereducedtoit.
JSONdatacanbeanyvalidJSONliterals, notonlyobjects; seeRFC[3]fordetails. AllRESTAPIrequestsmust
supplyvalidcredentials,andimplicitCORScredentialspassingisprohibited;thisrulesoutdifferent"JSONhijacking"
attacks,shouldtheyeverbecomepossibleagain.
### 5.4.2 text/plain
The plain text format is limited in what resources it can represent. It supports all scalar types (constant null is
encodedasanemptystring),andalsoarraysofscalartypes(valuesareseparatedbycommas',').
Iftheresourceisofasumtype, andthereisanambiguity(e.g. "false"couldmeantheconstantfalse, orastring
literal"false"),therequestisill-formedanddenied.
Ifyoufaceambiguities,orneedtoexpressvaluesofothertypes,youneedtouseJSON.
DLIREST-styleAPIReference:20221009T204818Z

### 5.4.3 application/x-www-form-urlencoded
TheURL-encodedformatislimitedinwhatresourcesitcanrepresent. Scalarvaluesarerepresentedbya'value'
keywithavaluecorrespondingtothetextualrepresentation,iftheyhaveone. Forexample,
value=1
value=false
value=Hello
Field-basedtypescanberepresentedintheformat
field1=value1&field2=value2&...
Thevaluesareagainintextualrepresentation.
Iftheresourceisofasumtype, andthereisanambiguity(e.g. "false"couldmeantheconstantfalse, orastring
literal "false"), you may append $ to the field name to indicate that the value is to be interpreted as a string, or
# to indicate that the value is to be interpreted specially (i.e. as a number, false, true, etc.; there's never an
ambiguitybetweenthose);forexample,
value#=1
indicatesthenumber1,while
value$=1
indicatesthestring"1". Likewise,in
field1#=value1&field2$=value2&...
field1isassignedanon-stringvalue,andfield2isassignedastringvalue.
Notethatthe$and#charactersneedtobeURL-encoded.
Ifyoufaceambiguitiesthissimpleconventioncan'tresolve,orneedtoexpressvaluesofothertypes,youneedto
useJSON.
## 5.5 PatchMIMEtypes
Datainthefollowingformatscanbespecifiedasarepresentationofachangetoresource(forPATCH)usingthe
Content-Typeheader:
### 5.5.1 application/json-patch+json
JSONpatchisthemainpatchformat. Itisacceptedbyallresourcesinallcircumstances. Otherpatchformatscan
bethoughtofasiftheywerereducedtoit. SeetheRFC[4]fordetailsandexamples.
Note that paths in JSON patch documents are JSON pointers, as per the JSON patch RFC [5], and not URIs.
Theyarenormallyeitherempty,orstartwithaslash(/),andneverendwithaslash. Theircomponentsarenever
percent-encoded(therearespecific'∼'escapesinJSONpointers[5]), andnomatrixURIsupportisinplace. Be
surenottoconfuseJSONpointersandrelativeURIs.
DLIREST-styleAPIReference:20221009T204818Z

## 5.6 OutputMIMEtypes 13
### 5.5.2 application/x-www-form-urlencoded
TheURL-encodedformatislimitedinwhatresourcesitcanrepresent.Itissimilartothefullresourcerepresentation,
but must include only the values you want to change. The field names (or the 'value' keyword) may be preceded
by'new_'toemphasizethatthisisthenewvalueyouwanttowrite. Ifyouwanttosupplythepreviousvalue, and
haveitchecked,youshouldprefixitwith'old_'. Notethatinsomecases,likechangingtheadministratorusername
password,youmaybeforcedtosupplytheoldpasswordvaluetobechecked.
When such patches are handled, first all 'old_' values are checked against the resource values, and the patch is
onlyappliedifallofthemmatch.
Forexample,thefollowingpatch:
old_name=admin&new_name=root&old_password=1234&new_password=4321
behavesasthoughyousuppliedthefollowingJSONpatchdocumentinstead:
[
{"op":"test","path":"/name","value":"admin"},
{"op":"test","path":"/password","value":"1234"},
{"op":"replace","path":"/name","value":"root"},
{"op":"replace","path":"/password","value":"4321"}
]
Requeststopatchanyobjectswithfieldsstartingwithold_ornew_prefixes(currentlynoobjectshavesuchfields)
areill-formed. Ifyouneedtoworkwithsuchobjects,youneedtosupplythepatchintheJSONpatchformat.
## 5.6 OutputMIMEtypes
Data in the following formats can be requested as a representation of a resource (usually for GET, but also other
methodsexceptDELETE)usingtheAcceptheader:
### 5.6.1 application/json
JSONisthemaininterchangeformat. Itisretrievableforallresourcesinallcircumstances. Objectswhicharenot
readable,ornotreachableduetodepthlimitations,willbereplacedtoJSONreferencestothem.
### 5.6.2 text/html
HTMListhebrowseroutputformat,whichenablesyoutointeractwiththeAPIusingthebrowser. Requestsgeneratedwiththebrowsercanserveastemplatesforyourownrequests,butyouarebynomeanslimitedbythem.
### 5.6.3 text/plain
Plaintextisthesimplehuman-readableformat,notintendedtobeprocessedautomatically. Youshouldnotrelyon
anyparticularformatforit.
DLIREST-styleAPIReference:20221009T204818Z

## 5.7 Preferenceindication
Somemethods(e.g. PUT,PATCHandPOSTtocreateresources)canreturnarepresentationoftheresult,butit's
optional. TheHTTPPreferheader[10]canbeusedtoindicateyourpreference. Requestswiththisheader
Prefer: return=representation
willreturntherepresentationofthecreatedormodifiedresource,whilerequestswiththeheader
Prefer: return=minimal
willreturnonlythestatuscodeandheaders.
TheserverwillrespondwithanappropriatePreference-Appliedheaderifthepreferencehasbeenunderstoodand
affectedtheoutput.
# 6 Extensions to the standard interfaces
## 6.1 Cross-siterequestforgeryprotection
ThelegacyAPIallowedtocreate"convenient"linksforactionslike"/outlet?a=OFF"or"/script.cgi?run100".
Such"convenience",however,comesatacost: if,whilebeingloggedintothecontroller,theuservisitsamalicious
pagewithsomethinglike
<img src="http://192.168.0.100/outlet?a=OFF"/>
or
<script src="http://192.168.0.100/outlet?a=OFF"></script>
orsimilar,thecorrespondingactionwillbetaken. Moremaliciouspageexampleswouldincludee.g. erasingsome
non-administrativeusers,etc. YoucouldreceiveanHTMLemailcontainingareferencetosuchan"image",andit
couldwork.
ThisisanextremecaseofavulnerabilitynamedCSRF(cross-siterequestforgery)[9]. Itisnotaffectedbyauthenticationorencryptionused. UsingPOSTtosendsuchrequestswouldonlybeabitmoresecure,asthosecanbe
imitatedbyanHTMLform,andtheusercouldbetrickedintosubmittingit.
ThelegacyAPIwillstayinplaceforthetimebeing,butthenewAPIisdesignedtomakeitmoreresistanttosuch
kindofattacks.
Inmodernbrowsers,XMLHttpRequestcanbeusedtoperformarbitraryrequests,butifthesender'sorigindoesn't
matchtherequesttarget,apreflightrequestissent,whichiscurrentlydeniedbythecontroller,soitcan'tbyitself
beusedtoforgearequest. SomeoldFlashpluginsdidn'tplaybytherulesandallowedarbitraryrequests,butthey
shouldbefixedbynow. So,theremainingsourcesofpotentially-problematicrequestsareHTMLforms,whichare
currentlylimitedtoGETandPOSTmethodswithContent-Typeofapplication/x-www-form-urlencoded(amongthose
supported by the REST API as inputcontenttypes). However, any state-modifying operation by default requires
additionalrequestheaderswhichindicatethatthesourceofoperationisnotanHTMLform:
X-CSRF: <any value>
or
DLIREST-styleAPIReference:20221009T204818Z

## 6.2 HTTPverbtunneling 15
X-Requested-With: XMLHttpRequest
Thefirstoptionissupportedbecauseit'sshorterandself-descriptive,andthesecondonebecauseitiswhatJava←(cid:45)
Scriptframeworksusuallysend.
MoresophisticatedCSRFprotectionmethods,likepassingatokenaround,arenotmuchmoreeffectiveandaren't
easytoimplementconsideringRESTdesignrestrictions.
Additionally,therequirementtoaddsuchheadersmaybeliftedifthefollowingoptionsareset:
• Relaxnon-HTMLmethodCSRFchecks(/restapi/config/relax_nonhtml_content_types/)
This setting allows HTTP clients to perform API requests with e.g. application/json or application/json-rpc
withoutaCSRFprotectionheader(suchcontentcurrentlycannotbesentviaanHTMLform).
• Relaxnon-HTMLcontenttypeCSRFchecks(/restapi/config/relax_nonhtml_methods/)
This setting allows HTTP clients to perform PUT/PATCH/DELETE API requests without a CSRF protection
header(suchrequestscurrentlycannotbesentviaanHTMLform).
Asofthetimeofthiswriting, thesesettingsdon'treducesecurity; however, moreHTMLformmethodsorcontent
typesmaybestandardizedinthefuture,makingthesetuplesssecure.
## 6.2 HTTPverbtunneling
IfyouhaveproblemssendingPUT,PATCHorDELETErequests,orifyouaresendingnon-idempotentPUTorD←(cid:45)
ELETErequests(seePUTandDELETEmethodsnotalwaysidempotentbelow),youcanwrapanarbitrarymethod
requestinaPOSTrequestusing,e.g.
POST /restapi/auth/users/2/ HTTP/1.0
X-HTTP-Method: DELETE
## 6.3 MatrixURIsandworkingwithmultipleresourcesinparallel
MatrixURIs[1]areawayofencodingURI-segment-specificrequestparametersinthesegment(URIpartdelimited
by'/')itself. IntheAPI,amatrixURIsegmentdefinesaselectorwhichperformsfilteringofmatchingsubresources.
Considerthefollowing'collection'ofresources,eachofwhichisthecurrentphysicalstateoftheappropriateoutlet:
/restapi/relay/outlets/0/physical_state/
/restapi/relay/outlets/1/physical_state/
...
/restapi/relay/outlets/7/physical_state/
Youcanmanipulatethem,oranysubsetofthem,asawhole,byreplacing'0','1',etc.(theoutletindex)withamatrix
URIselector. Herearesomesamples:
• Physicalstatesofalllockedoutlets:
/restapi/relay/outlets/all;locked=true/physical_state/
• Physicalstatesofoutlets#1,#3,#5:
/restapi/relay/outlets/=0,2,4/physical_state/
• Physicalstateofthesoleoutletwhosenameis'lamp':
DLIREST-styleAPIReference:20221009T204818Z

/restapi/relay/outlets/name=lamp/physical_state/
• Physicalstatesofalloutletswhosenameis'lamp'or'server':
/restapi/relay/outlets/all;name=lamp,server/physical_state/
• CycleallunlockedONoutlets(usingPOST):
/restapi/relay/outlets/all;physical_state=true;locked=false/cycle/
MatrixURIsegmentparsingisactivatedbythepresenceof'=',';'or','. Ifyouneedtoincludetheminaregularpath
segment(youshouldn'tneedtointhecurrentdatamodel),youneedtopercent-encodethem.
A matrix URI segment contains one or more parts, separated by an (unescaped) ';'. The first part may be a filter
policy,andmustbefollowedbya';'evenifnootherpartsarepresent. Thesupportedfilterpoliciesare:
• all: theoperationwillbeperformedonallmatchingresources,andtheresponsewillbea207Multipleresults
response;evenifnoresourcesmatch,theresultwillbesuccessful;
• one: the operation will expect exactly one resource to match; if no resources are found, 404 Not found
is returned; if multiple resources are found, a 300 Multiple choices response, mentioning the options, is
presented;
Allothermustpartscontainkey=valueentries,themeaningofwhichdependsonthekey:
• ifkeyisempty(like'=0,2,4'),thevalueisacomma-separatedlistofkeystomatch;ifoneofsuchvaluesisthe
emptystring(e.g.consider"=,name"oreven"="),itcorrespondstoapseudo-resourcecontainingthe(integer
or string) index of the currently matched (parent) element; additionally, if no filter policy is set, it defaults to
'all';
• ifkeyisnonempty,itistreatedasthenameofthefieldofresourcesbeingmatched; thevalueisacommaseparatedlistofvaluestomatch;additionally,ifnofilterpolicyisset,itdefaultsto'one'.
Ifmultiplekey=valuepartsarespecified,onlytheresourcesmatchingallofthemareselected. Forexample,
/restapi/relay/outlets/=0,2,4;locked=true/physical_state/
willselectphysicalstatesoflockedoutlets,butonlyamongoutlets#1,#3and#5.
TheseseeminglycomplexrulesallowforshortURIsforcommonusecases.
## 6.4 Linkrelation'templated'
## 6.5 Responsedepthlimiting
Inmanycases,youdon'twanttoseealloftheoutputofarequest.Range:bytesmakesnosenseformostAPIcalls.
Youlikelywon'tgetawell-formedHTMLorJSONdocumentifyourequestabyterange. Asresourcesarearranged
inanhierarchy,thenaturalwaytodooutputlimitingisbyreferringtoadepthlevelinthishierarchy. Youcanusethe
Rangeheaderwithadli-depthrangeunittoperformlimiting. Whenalevelofhierarchyisnotdescendedinto,the
valueisreplacedbyaJSONreferencetoit,e.g.:
... "relay": {"$ref":"relay\/", "title":"Relay object"}, ...
The$refparameterisarelativeURI(nottobeconfusedwithaJSONpointer)tothevalue.
Forexample,
DLIREST-styleAPIReference:20221009T204818Z

7Deviationsfromstandardsandcommonpractices 17
Range: dli-depth=1
willgiveyoutheimmediatechildresourcesofthisresourceasreferences,and
Range: dli-depth=0
willgiveyou
{"$ref":"","title"="..."}’
iftheresourceexists.
Thedefaultis:
Range: dli-depth=infinity
whichmeansinfinitedepth.
The limiting is only supported for non-HTML output formats (JSON, plain text). HTML output depth is contextdependent,butcanbethoughtofasfixedat1inmostusecases.
# 7 Deviations from standards and common practices
## 7.1 Nonstandard207Multipleresponsesformat
TheWebDAVRFC[6],whereHTTP207Multipleresponsescodeisdefined,isXML-centric,andrequiresthatthe
responsetypebeXML.TheAPIgeneratesthiscodewhenprocessingmatrixURIrequests,andproducesoutputin
theformatrequestedbytheclientintheAcceptheaderinstead,becausewebelieveittobemoreuseful. However,
thespiritoftheRFCispreservedasmuchaspossiblesoasnottointroducecomplexity.
The HTML-formatted response follows the format defined in [6], but instead of custom elements, it creates div
elementswithcorrespondingclasses.
The JSON-formatted response contains an array of responses. The HTTP response will contain corresponding
"Link: <...>, rel=item" headers which can be used to gain the information on what resource each response is
returnedfrom.
## 7.2 PUTandDELETEmethodsnotalwaysidempotent
PUTisnormallyanidempotentmethod,butitmayinteractwithmatrixURIsinapossiblyunexpectedmanner. For
example,consider
PUT /restapi/auth/users/name=fred/name/ HTTP/1.0
...
value=joe
This request will rename user 'fred' to 'joe'. It is all fine and the request will work as expected. However, it won't
technically be idempotent because /restapi/auth/users/name=fred/ will no longer resolve (Fred is now Joe). This
wouldalsohappenifyouusedPATCH,butPATCHisn'texpectedtobeidempotent,whilePUTis.
Referringtothatuserbytheirsequentialnumberwouldmaketherequestidempotent:
DLIREST-styleAPIReference:20221009T204818Z

PUT /restapi/auth/users/2/name/ HTTP/1.0
...
value=joe
Sucharequestwouldbeidempotent.
DuetotheJSONrepresentationofdataandexpressingmanipulationswithitusingJSONpatch,it'snotpossiblefor
arequestlike
DELETE /restapi/auth/users/2/ HTTP/1.0
to be idempotent: deleting a value from a JSON array causes reindexing of successive elements, so user #3
becomes user #2, user #4 becomes user #3, etc. You should not rely on DELETE to be idempotent in this case.
Wehavenoconceptof'identity'forparametersstoredinJSONarrays.
Abetterwaytodeleteausercouldbebyname,e.g.
DELETE /restapi/auth/users/name=fred/ HTTP/1.0
Sucharequestwouldbeidempotent(itwouldstillhavethereindexingsideeffectthough).
If you really want to change properties of objects by which you selected them in a matrix URI, or delete objects
by their sequential number, and want to notify any intermediaries that the request is not actually idempotent, you
shouldwraptheminPOSTrequestsusingHTTPverbtunneling.
## 7.3 Semanticallyside-effect-freecallsstillneedPOST
All function calls are performed by POST requests to the function's URI. However, some of these functions, like
gettingahistoryofameter'svaluesoveraperiodoftime,aresemanticallynilpotent(havenosideeffects),soGET
couldbeused. Unfortunately,mostofthesefunctionshavearguments,whicharetobesentintherequestbodyfor
contenttypedetectiontobemeaningful,andsendingabodyinaGETrequestisnotstandard. So,POSTisused
instead.
## 7.4 PATCHisallowedonread-onlyresources
WeallowPATCHtooperateonresourceswhichareread-onlybynature, orwritestowhicharedeniedbypolicy.
Thereasonforthisisthatapatchdoesn'thavetocontainmodifyingoperations,justtestoperations,andmayeven
notcontainanyoperationsatall,inwhichcasesuchresourcesarevalidPATCHtargets.
## 7.5 SomePATCHoperations
The JSON patch "move" and "replace" operations are specified [4] to be functionally identical to a "remove" operation, followed by an "add" operation. There are obvious problems when attempting to apply such principles to
additionallyconstrainedobjectswithinternalbehaviour.
Someobjects(e.g. theadministrativeuser)cannotbesubjectedtoa"remove"operation,andattemptingtomove
theme.g. forsimplereorderingmayfail. Additionally,suchoperationswilleraseanyinternalstateoftheremoved
object,soe.g. youcansafelymoveorreplaceonlyadisabledAutoPingentry.
Additionally, heterogeneous containers cannot have their fields removed, so such "replace" behaviour would be
uselessforthefields.
DLIREST-styleAPIReference:20221009T204818Z

## 7.6 Templatedand'hackable'URIs 19
## 7.6 Templatedand'hackable'URIs
StrictadherencetoprinciplesofRESTwouldrequireallpossiblelinkstobeexposedtotheclient,butit'ssimplynot
feasible to enumerate all use cases for matrix URIs. Technically we could give you so-called opaque URIs for all
resourcesfromtheentrypoint,like:
<a href="/restapi/55237aa40998e90a093e8190cd8d3bf8/" rel="dli-outlet">Outlet 1 state</a>
Wecoulddocumentthelinkrelations, contentsubtypesandallthat, andbecomemoreHATEOAScompliant, but
thisdoesn'tseempractical. Rather,wechoosetomakeURIstructurerepresentthedatamodel,andrelyonyouto
applycommonsenseandpatternsdiscussedinthisreferencetotheinformationyouobtainfromtheAPItogenerate
URIs.
IncasesomepartoftheURIschemechanges,weexpecttobeabletoemulateexistingresourcelinks,orredirect
you from old locations using standard HTTP 30x Redirect responses, so you will at least be notified that the U←(cid:45)
RI scheme has changed (correctly configured clients would understand the redirect). Resources that were once
presentbuthavebeendiscontinuedwouldyield410GoneHTTPresponses.
DLIREST-styleAPIReference:20221009T204818Z

# 20 REFERENCES
References
[1] T.Berners-Lee. MatrixURIs–IdeasaboutWebarchitecture,December1996. 15
[2] T.Berners-Lee, R.Fielding, andL.Masinter. UniformResourceIdentifier(URI):GenericSyntax. RFC3986
(INTERNETSTANDARD),January2005. UpdatedbyRFCs6874,7320. 1,10
[3] T.Bray. TheJavaScriptObjectNotation(JSON)DataInterchangeFormat. RFC7159(ProposedStandard),
March2014. 2,11
[4] P.BryanandM.Nottingham. JavaScriptObjectNotation(JSON)Patch. RFC6902(ProposedStandard),April
2013. 12,18
[5] P. Bryan, K. Zyp, and M. Nottingham. JavaScript Object Notation (JSON) Pointer. RFC 6901 (Proposed
Standard),April2013. 12
[6] L.Dusseault.HTTPExtensionsforWebDistributedAuthoringandVersioning(WebDAV).RFC4918(Proposed
Standard),June2007. UpdatedbyRFC5689. 17
[7] R. Fielding and J. Reschke. Hypertext Transfer Protocol (HTTP/1.1): Authentication. RFC 7235 (Proposed
Standard),June2014. 11
[8] J.Franks,P.Hallam-Baker,J.Hostetler,S.Lawrence,P.Leach,A.Luotonen,andL.Stewart. HTTPAuthentication: BasicandDigestAccessAuthentication. RFC2617(DraftStandard), June1999. UpdatedbyRFC
7235. 11
[9] OWASP. Cross-siterequestforgery(CSRF),December2014. 14
[10] J.Snell. PreferHeaderforHTTP. RFC7240(ProposedStandard),June2014. 14
[11] Wikipedia. Representationalstatetransfer–Wikipedia,thefreeencyclopedia,December2014. 1
DLIREST-styleAPIReference:20221009T204818Z
