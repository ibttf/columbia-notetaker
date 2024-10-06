import os
import re
import markdown2
import google.generativeai as genai
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel, Field
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')
client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
    ),
    mode=instructor.Mode.GEMINI_JSON,
)

class GoogleDocsNotes(BaseModel):
    title: str = Field(description="Title of the class session")
    summary: str = Field(description="Brief summary of the class content")
    notes_content: str = Field(description="Detailed notes content in markdown format")

def generate_class_notes(transcript: str) -> GoogleDocsNotes:
    system_prompt = """
    You are an AI assistant that generates comprehensive class notes from a given transcript.
    The notes should be formatted in markdown.
    """
    
    user_prompt = f"""
    Please analyze the following class transcript and generate detailed notes:

    {transcript}

    Create well-structured notes with the following guidelines:
    1. Use a clear hierarchy with headers and subheaders (use # for main headers, ## for subheaders, etc.)
    2. Include timestamps for all bullets in your notes (format: [HH:MM:SS] or [MM:SS] or [H:MM:SS])
    3. Use bullet points for lists
    4. Bold important terms or concepts
    5. Include a brief summary at the beginning

    Format the notes in markdown so they can be easily converted to HTML.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_model=GoogleDocsNotes
    )

    return response

def timestamp_to_seconds(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    else:
        return 0  # Return 0 for invalid formats

def create_html_content(notes: GoogleDocsNotes, base_url: str):
    def replace_timestamp(match):
        timestamp = match.group(1)
        seconds = timestamp_to_seconds(timestamp)
        return f'<a href="{base_url}&start={seconds}" target="_blank">[{timestamp}]</a>'

    # Replace timestamps in the markdown content
    notes_content_with_links = re.sub(r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]', replace_timestamp, notes.notes_content)

    # Convert markdown to HTML
    html_content = markdown2.markdown(notes_content_with_links)

    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{notes.title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>{notes.title}</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p>{notes.summary}</p>
        </div>
        <div class="notes-content">
            {html_content}
        </div>
    </body>
    </html>
    """
    return full_html

@app.route('/generate_notes', methods=['POST', 'OPTIONS'])
def generate_notes():
    print("I'm here")
    data = request.json
    # transcript = data.get('transcript')
    transcript = """
	
Powered by Panopto

Fall 2024 - COMSE6998_008_2024_3 - TOPICS IN COMPUTER SCIENCE
chevron_right
COMSE6998_008_2024_3 - TOPICS IN COMPUTER SCIENCE
share
Help
arrow_drop_down
Sign out
Search this recording
search
Details
Captions
Discussion
Notes
Bookmarks
Hide
Ronghui Gu: Okay, right? So I just use my laptop phone
0:07
Ronghui Gu: to share this with.
0:12
Ronghui Gu: it's like.
0:15
Ronghui Gu: yeah.
2:27
Ronghui Gu: and they're completely enabled
2:30
Ronghui Gu: computers.
2:37
Ronghui Gu: So
4:22
Ronghui Gu: oops
4:32
Ronghui Gu: one second. Okay, let's see, slides.
4:34
Ronghui Gu: Let me see.
4:37
Ronghui Gu: That's see.
4:39
Ronghui Gu: Shit.
4:42
Ronghui Gu: maybe
4:49
Ronghui Gu: oops.
5:03
Ronghui Gu: Excellent.
5:18
Ronghui Gu: We need this changes.
5:21
Ronghui Gu: Let's do so.
5:24
Ronghui Gu: oops
5:27
Ronghui Gu: because
5:46
Ronghui Gu: it's cool.
5:53
Ronghui Gu: Let's see.
5:59
Ronghui Gu: this is
7:11
Ronghui Gu: awesome. Yeah, sure
7:34
Ronghui Gu: working.
7:42
Ronghui Gu: So
7:45
Ronghui Gu: no one
8:25
Ronghui Gu: sick.
8:27
Ronghui Gu: What's the communications?
8:28
Ronghui Gu: We should lose this stuff already.
8:30
Ronghui Gu: Think this might be good?
8:53
Ronghui Gu: Hello!
9:08
Ronghui Gu: Can you hear me
9:09
Ronghui Gu: able to see the chassis.
9:23
Ronghui Gu: So
9:26
Ronghui Gu: Hello! Hello! Everyone so to make this class and make a hybrid class, such as students do not have visa issues. So that's why I need to hold some lectures. On campus. And
9:28
Ronghui Gu: glad to see you guys. And so this already, the 1st lecture. And we're gonna talk cover, solidity.
9:43
Ronghui Gu: the high level programming languages that are you that is used for writing smart contrasts on the Etherne blockchain.
9:51
Ronghui Gu: Okay, we'll start with some examples.
10:00
Ronghui Gu: Give me one second.
10:15
Ronghui Gu: It's very like.
10:28
Ronghui Gu: yeah. So this is the example with smart contact. We had deployed before.
10:31
Ronghui Gu: right? Smart contrast for developing a domain name system. Right? So this actually is was written in solidity. The language that we're gonna cover today
10:37
Ronghui Gu: and it so this is solid code. And here, this contract keyword, right? It's used to declare a new contract. And this is company. And here we define a data structure called name entry, right, which has 2 views. The 1st one is the owner, right size, address
10:53
Ronghui Gu: and the second field is value record representing the IP address, right of the domain person, one domain, and this time is advice sort of true right? And then we, so this is
11:11
Ronghui Gu: this is a structure. And then
11:27
Ronghui Gu: we have a actually kind of like a global variable.
11:31
Ronghui Gu: It's highly mapping from by 32 to name entry. Okay, name entry is defined here.
11:35
Ronghui Gu: And so this is a function to register a domain right?
11:43
Ronghui Gu: We so we we use this global variable data to check that. Well, this domain name has not been registered yet. Right? Which is equal to 0. And here message doll value. This message is a a global
11:49
Ronghui Gu: variable that we can refer to representing, kind of like, the the message that triggered this smart contracts a message that volume
12:06
Ronghui Gu: meaning the the users carried by this message. And if that's enough easier to pay this 100 way for registration fee. And then we're gonna
12:16
Ronghui Gu: here. We're gonna set the domain owner
12:30
Ronghui Gu: to be the message dot sender
12:34
Ronghui Gu: right? And then here, this image register. This is actually, it's a long mess, right? This image is to log this bus right
12:37
Ronghui Gu: here. In this function will basically set the the owner of the domain.
12:48
Ronghui Gu: And this is a domain name update function. Right here. We also need to check that. Well, we have enough either to pay the fee.
12:55
Ronghui Gu: And
13:06
Ronghui Gu: then we also need to check about the
13:12
Ronghui Gu: the message center equals to the
13:14
Ronghui Gu: owner of the domain right? Only the owner of the domain have this domain's information right?
13:18
Ronghui Gu: And if this is the case and we're gonna update the the value and owner of the domain information.
13:24
Ronghui Gu: This is a lookout function. That's we. Simply we simply return the corresponding IP address of the current of the domain.
13:33
Ronghui Gu: These are examples, smart contrast, written in solidity that we covered in the previous lecture.
13:43
Ronghui Gu: And in this lecture we're gonna dive deep into the solid language.
13:50
Ronghui Gu: Any questions so far
13:56
Ronghui Gu: move forward.
14:03
Ronghui Gu: Yeah, first, st what is solidity? Solidity is a major program language providing smart contract for easier on blockchain.
14:04
Ronghui Gu: Actually, there are other high level languages that we can also use to write smart contracts right on different blockchain platforms. Even on either platform there are different. High Level program languages
14:11
Ronghui Gu: and facility is still the mostly used one on Israel, and also the mostly used one for for all. All block shares that we'll see
14:28
Ronghui Gu: and selected is contact oriented right in the sense as well. Actually, it's it's you can see as well is the the pieces. Codes are groups into context, right? That's you can view it as a major building components
14:40
Ronghui Gu: for
14:57
Ronghui Gu: building comp components, that is that we use solidity to to write.
15:00
Ronghui Gu: And so it is also steadily tight.
15:06
Ronghui Gu: was was in the meaning of step away. Tact?
15:09
Ronghui Gu: That would be great.
15:18
Ronghui Gu: Yeah.
15:21
Ronghui Gu: yeah. So a type means as a once, a location type is determined. It's clear it can, cannot be changed by his, and everything is the type is determined
15:22
Ronghui Gu: during the compilation time.
15:36
Ronghui Gu: Right? It's not determined at wrong time. Right, for example, like a python, is not separate time in the sense that you you have a variable right. You can assign a string to it, and later you can assign anything right? So the the type of variables not determined during the conversion time it's determined during the wrong time
15:38
Ronghui Gu: while solving was all this has determined to add the compilation time.
15:59
Ronghui Gu: and it has support inherits inheritance libraries and many program features that we're gonna cover later
16:05
Ronghui Gu: and
16:13
Ronghui Gu: the smart contracts written by solid. You can view them as Api micro services on Web 2.
16:14
Ronghui Gu: It's kind of like
16:21
Ronghui Gu: and view them as interfaces that can be publicly accessible to everyone that can call
16:23
Ronghui Gu: by, if basic call by other contracts we can view them as called, can be called as a guys, basically.
16:30
Ronghui Gu: And well, the actual code will be understood on the Islam watch.
16:39
Ronghui Gu: Okay? So that's
16:47
Ronghui Gu: look at another example, contact called storage
16:51
Ronghui Gu: and this is a very simple smart contracts and written the file storage style. SOLS. OL. Is a file extension name for solid programs.
16:55
Ronghui Gu: And and this smart podcast is used to store and retrieve a value
17:07
Ronghui Gu: very reasonable one.
17:11
Ronghui Gu: Right here you can see the
17:14
Ronghui Gu: the contract.
17:17
Ronghui Gu: So at the the 1st lie.
17:18
Ronghui Gu: It's pragma solidity 0 point 5.1. This defines a version, the solid version that values.
17:21
Ronghui Gu: And so then we have
17:31
Ronghui Gu: contact keyboard. Right?
17:34
Ronghui Gu: Means I'm gonna define a contract with whose name is storage.
17:36
Ronghui Gu: right? And then we have a
17:42
Ronghui Gu: this line declares this volume right.
17:45
Ronghui Gu: that we've got a store on the trip, and it's time to string
17:49
Ronghui Gu: pretty straightforward, right?
17:52
Ronghui Gu: Quite similar to many other high level program launches.
17:55
Ronghui Gu: And one thing, yeah, here. This. This indicates the site version.
17:59
Ronghui Gu: And here
18:05
Ronghui Gu: is a 1st of all, it's a kind of like a global variable. We call it a state. Variable.
18:07
Ronghui Gu: Right means that all the functions within this contrast have access. This
18:12
Ronghui Gu: right? Like the the kind of like, the the global variable for for for a program, right? Things like that. And here the state variable. We're so guess where the state variable will be stored
18:18
Ronghui Gu: right in the-. In the
18:38
Ronghui Gu: last lecture we talked about. So either way.
18:40
Ronghui Gu: each contract has a story right? Each contract has a story. State variables will be stored on that per accounts storage
18:43
Ronghui Gu: right? And it will. It will be persistent on the block.
18:53
Ronghui Gu: Eddie.
18:59
Ronghui Gu: any questions so far?
19:00
Ronghui Gu: Yeah. And so then for this
19:10
Ronghui Gu: contracts, we define the 1st fun function to raise a volume right from from the storage contract. Right? So
19:12
Ronghui Gu: here we have a function, gets public view, return string, return volume right? If we ignore the part after the get
19:23
Ronghui Gu: right, the function name is pretty simple. Right now, function, get return volume right? This value is saver
19:32
Ronghui Gu: as a resonating for this public
19:38
Ronghui Gu: viewer returns bye.
19:41
Ronghui Gu: it's public
19:43
Ronghui Gu: keyword defines the visibility of this function
19:45
Ronghui Gu: bye
19:48
Ronghui Gu: public makes us
19:49
Ronghui Gu: it. These function can be accessed by actionable contracts.
19:53
Ronghui Gu: And
20:00
Ronghui Gu: can this function be accessed by, let's say, out of, can this function be accessed by other functions within the same contract?
20:01
Ronghui Gu: Yes, right? So probably this basically mean that this function can be accepted by both internal and external functions.
20:09
Ronghui Gu: Right? External means, the functions from other countries.
20:16
Ronghui Gu: Okay, so that was the meaning for this view?
20:20
Ronghui Gu: View? A view only right? They say real, only
20:24
Ronghui Gu: right means that this function will not modify
20:28
Ronghui Gu: the the asset storage, and so on
20:32
Ronghui Gu: and
20:39
Ronghui Gu: returns basically defines a.
20:40
Ronghui Gu: the return time of the assumption.
20:45
Ronghui Gu: Okay.
20:49
Ronghui Gu: this is losing time.
20:49
Ronghui Gu: And then we can have the similar set function
20:53
Ronghui Gu: here, this set function public. Can we add a view keyword here?
20:58
Ronghui Gu: No, right? Because this also gonna update the story right? It's now read. Only so you should now put the view keyword here. So you may find as well, actually, it's many kind of like the the most of the language that actually are questioner with other languages. But there are some
21:05
Ronghui Gu: unique features. Right? You can see, for example, this view, right? Obviously, it's not that common. And in a language for function. We we want to define about this functions. Read only.
21:25
Ronghui Gu: oh, no. So why? Why one have this highlight? You can still have the the control, the visibility of the function. We also want to control
21:38
Ronghui Gu: the the memory behavior.
21:48
Ronghui Gu: Why
21:53
Ronghui Gu: go ahead?
21:54
Ronghui Gu: Yeah. 1st of all, yes, but last guess. Second also make it more secure. Right? So when you define function, and is 6,
21:56
Ronghui Gu: if it's it is expected to be real. Only then we add this queue
22:05
Ronghui Gu: right to avoid, as if some some mistakes that will accidentally modify some States.
22:12
Ronghui Gu: And here we have set function. And here we pass. Arguments, we use a dash in front of it to annotate as well. This is a
22:23
Ronghui Gu: this is the arguments or temporary variables.
22:32
Ronghui Gu: Okay, then.
22:36
Ronghui Gu: we have the
22:38
Ronghui Gu: this constructor function.
22:40
Ronghui Gu: right?
22:42
Ronghui Gu: This kind of structure simply initiates the value for
22:43
Ronghui Gu: for initiate this volume bar.
22:47
Ronghui Gu: bye.
22:52
Ronghui Gu: this touch constructor will only be called what
22:53
Ronghui Gu: during the appointment?
22:57
Ronghui Gu: No, so it's not called. It will only be called once during the deployment, and it, its visibility must be said to be public
23:00
Ronghui Gu: bye.
23:13
Ronghui Gu: So that's a full contract for this very simple storage smart contracts.
23:14
Ronghui Gu: So
23:22
Ronghui Gu: here.
23:23
Ronghui Gu: let's see a little bit different.
23:26
Ronghui Gu: Why so? And here.
23:28
Ronghui Gu: for this returns value, we can add a keyword memory.
23:32
Ronghui Gu: Maybe that's well, the
23:37
Ronghui Gu: return value gotta be stored
23:40
Ronghui Gu: memory. But my memory is
23:43
Ronghui Gu: a difference
23:46
Ronghui Gu: I will say storage class of or storage type for solving language. Right? This is different from storage. My storage is either blockchain, and it's persistent. Right per account has a storage, and this memory sits in evm
23:49
Ronghui Gu: means that when miner right ask you or validates this, the exscription of the smart card. It will run this program on top of Evm. And this memory sits on in the Evm.
24:07
Ronghui Gu: And it will not be stored on the blockchain.
24:20
Ronghui Gu: Right? Means that after the function call after this escalation well, this, this the volume will will go.
24:24
Ronghui Gu: It's probably.
24:32
Ronghui Gu: and if we do not put a memory here. Right? For let's say for argument, let's say
24:36
Ronghui Gu: for this State variable. They are always stored in storage. Right? For let's say for arguments
24:43
Ronghui Gu: for local, for local variables. They will 1st be trying to be stored on stack.
24:49
Ronghui Gu: which is also another type of storage Edm, and if you for simple data, we will cover all this later. And if you want want the variable to be stored on memory, you use this memory field.
24:55
Ronghui Gu: If you want a variable to be sort out storage you, you change this memory to storage.
25:11
Ronghui Gu: otherwise you will use a default setup.
25:17
Ronghui Gu: And
25:25
Ronghui Gu: here, right? We can also put memory
25:26
Ronghui Gu: for the arguments right? Maybe as well, this arguments will be stored in memory of email.
25:30
Ronghui Gu: And here for this state variable. We can also add a keyword public
25:39
Ronghui Gu: right? When we add this public key will to a saver, what means that means that this
25:43
Ronghui Gu: this variable can be accessed by
25:49
Ronghui Gu: can can be publicly accessed.
25:53
Ronghui Gu: Right? That's the case. We don't need a gas function.
25:56
Ronghui Gu: You don't need a gap function to access it right? At some point.
26:00
Ronghui Gu: you can simply access it through value with current systems.
26:04
Ronghui Gu: Go ahead. Oh, I would do one.
26:09
Ronghui Gu: Yeah, usually we would. We would not store arguments on
26:16
Ronghui Gu: in memory, as as I mentioned. So let's say arguments of this functions by default will be stored on stack right? But if you want to change the change it, you you can use this keyword memory, like maybe some local variable simple
26:21
Ronghui Gu: with symbol type. There by default is their store in stack. But you can use this memory keyword to store it in the in the memory. You can also use a storage keyword right to store it on the blockchain on 0.
26:38
Ronghui Gu: Any other questions.
26:54
Ronghui Gu: So could a function input arguments, storage type. Also.
26:56
Ronghui Gu: you can put a storage you can put a storage key with there. Yeah, but it's not.
27:02
Ronghui Gu: It's it's not recommended
27:08
Ronghui Gu: another purchase.
27:18
Ronghui Gu: Okay? And also here. Firstly, we initially initiate this value in a constructor that function right after, when we define it as a state variable, we also initiate
27:24
Ronghui Gu: during the Declaration.
27:37
Ronghui Gu: Yeah, so these are
27:43
Ronghui Gu: some examples. Now let's dive deep into the language features.
27:46
Ronghui Gu: There's some
27:51
Ronghui Gu: many, many definitions. Right? We'll go through them. So 1st of all, we gotta talk about the volume types
27:53
Ronghui Gu: supported by Solvia team.
28:00
Ronghui Gu: Okay, first, st definitely, is support editors.
28:03
Ronghui Gu: Bye.
28:07
Ronghui Gu: we have int you int U, ins. 8, right? Int is the default
28:07
Ronghui Gu: integer, and actually is equal to int. 256.
28:13
Ronghui Gu: Right issue are the same.
28:17
Ronghui Gu: and you in Union 200 250 is not the same. You can have you in 32, right, you in 8, Union 16, and so on.
28:20
Ronghui Gu: And then we also have a bully, which is full.
28:29
Ronghui Gu: and also have address.
28:33
Ronghui Gu: And same with actually the underlying same same with buy 32, right, 32 is a 32 buys
28:37
Ronghui Gu: simple data type.
28:46
Ronghui Gu: But but for address, right, there are many kind of like
28:49
Ronghui Gu: attributes and functions that that it can call can be called right using the for the address side. Right
28:54
Ronghui Gu: here. There are a few with us.
29:03
Ronghui Gu: 1st is address stall balance.
29:06
Ronghui Gu: So guess what what this attribute means.
29:10
Ronghui Gu: yeah, the amount of waste of this
29:19
Ronghui Gu: address, the model waste
29:23
Ronghui Gu: in
29:27
Ronghui Gu: all about this aspect.
29:30
Ronghui Gu: And so here we don't have parenthesis, because this is a attribute.
29:32
Ronghui Gu: Right? So simply, you can simply accept it by address. Stop balance. It's not a function call.
29:38
Ronghui Gu: And then we have address doll set and the address doll transfer.
29:44
Ronghui Gu: So basically transfer some amount of
29:49
Ronghui Gu: they say we transfer some amount of either. Right?
29:56
Ronghui Gu: So the differences between send and transfer
30:00
Ronghui Gu: are
30:03
Ronghui Gu: us send
30:05
Ronghui Gu: will.
30:07
Ronghui Gu: We always have returned.
30:09
Ronghui Gu: and and it returns. One means well, this set succeeds right. If it returns, 0 means that it says, fail.
30:11
Ronghui Gu: right transfer is that if it failed well, this this the the contract will will abolt.
30:20
Ronghui Gu: That's the difference between these 2 functions.
30:28
Ronghui Gu: And then we also have address style call
30:30
Ronghui Gu: right? This basically will invoke invoke a function as another address.
30:35
Ronghui Gu: Basically, this gonna in basic kind of kind of like, you've got invoke a function. Call
30:44
Ronghui Gu: on this address.
30:50
Ronghui Gu: We have address.com, or 80, let's say, address one.com. It will call up
30:53
Ronghui Gu: function, address one.
30:59
Ronghui Gu: and we can put call data
31:02
Ronghui Gu: as Arnold's
31:04
Ronghui Gu: put our call data, and then later, we'll we'll we'll we'll show how to contract this kind of like, call it.
31:06
Ronghui Gu: And so this we can. Well, for when we write smart contracts inside, we can simply call function like we call function in
31:15
Ronghui Gu: high side. So on right, we can of function within a small project. And then this is a kind of like a a cool pointer.
31:25
Ronghui Gu: Right? It's kind of like it gives the flexibility of of the program. Right? You can power arbitrary
31:34
Ronghui Gu: can call function on arbitrary address. And you can. You should you should put the call data into the the arguments, right? The call data should basically have just the function signature. So
31:43
Ronghui Gu: this kind of is kind of like the the go pointer. Ec program. C, right?
31:57
Ronghui Gu: You can call a function given address or given
32:03
Ronghui Gu: address give you the flexibility. But of course it's not as it.
32:10
Ronghui Gu: So that's okay.
32:17
Ronghui Gu: And here we have address of static call
32:18
Ronghui Gu: address. That call means as well. You're gonna it's SIM. It's similar to address or call
32:24
Ronghui Gu: difference is that, sir?
32:29
Ronghui Gu: Well.
32:32
Ronghui Gu: assume this call will not modify the States.
32:33
Ronghui Gu: It's kind of like a view.
32:38
Ronghui Gu: Your keyboard thing, right?
32:40
Ronghui Gu: Basically as well. The function call
32:41
Ronghui Gu: in the in our address should be a view only
32:44
Ronghui Gu: country, right? If it's modified states. Well, the small contract will be will box.
32:48
Ronghui Gu: So basically, I have some confidence over
32:57
Ronghui Gu: this function call, and the last one is address of delegate. Call
33:00
Ronghui Gu: the differences between this one and the address of call. It does.
33:08
Ronghui Gu: it will load the code from another contract to the current contract and the
33:12
Ronghui Gu: Cards
33:18
Ronghui Gu: busy. You probably use the current environment rather than the other contracts.
33:20
Ronghui Gu: Right? These are, this is address, right? It's a very unique data types, almost the same without
33:28
Ronghui Gu: with other data in in
33:38
Ronghui Gu: other program numbers. Well, address, you can see is unique, right? Pretty, unique. And is you used for smart contracts as well? Right?
33:41
Ronghui Gu: And then we have fixed size arrays.
33:55
Ronghui Gu: face size already, such as by 32. So by 32 is, you can view it as face size rate, right? That we have size difference. 5 Byte in this data set
33:58
Ronghui Gu: and
34:16
Ronghui Gu: beyond simple data types. We also have reference types or complex
34:17
Ronghui Gu: well, switches to our complex app.
34:25
Ronghui Gu: we have strings right like here.
34:29
Ronghui Gu: Stream name right? We have a
34:32
Ronghui Gu: variable same. Which type of string and we have straws like this
34:35
Ronghui Gu: struct-struct burst
34:40
Ronghui Gu: right? Struct person. We define, we can define struct name, person, and has 2 fields, right age, which is, whose type is you? Each 128, and a name whose time is straight. This is struct. And then we also have array
34:43
Ronghui Gu: like person 10 public stewards.
34:59
Ronghui Gu: There's
35:02
Ronghui Gu: defines a rate with face size, 10 right?
35:03
Ronghui Gu: And and each analyst has a type person.
35:07
Ronghui Gu: and
35:12
Ronghui Gu: the visibility is public.
35:13
Ronghui Gu: This is a kind of like a state that our role can be accessed publicly, and it's a fixed size of right. Each animal has a kind of person.
35:15
Ronghui Gu: What about the last one
35:23
Ronghui Gu: versa?
35:25
Ronghui Gu: Swear
35:27
Ronghui Gu: other people? This is also great right? But it's not a
35:29
Ronghui Gu: fixed size array, right? So this size can be determined can be changed dynamically.
35:33
Ronghui Gu: Right at the beginning there is a empty array, right? So we can use push
35:41
Ronghui Gu: to a pen
35:46
Ronghui Gu: value to this array.
35:48
Ronghui Gu: and we can just pop. And we can access the the
35:51
Ronghui Gu: this, or we're using index
35:57
Ronghui Gu: right? And the
36:00
Ronghui Gu: for this array, it also has a attribute called last right? We can check the last of the array
36:02
Ronghui Gu: any any questions so far.
36:11
Ronghui Gu: Yeah. So the next one is magic.
36:19
Ronghui Gu: Alright.
36:22
Ronghui Gu: so this is a declaration of the map. Right menu, basically store key value pairs and the key value types are defined here. Right here. Address from address to you, 8, 256 means as a key.
36:24
Ronghui Gu: Keys. Have this address. Well, always have, as you need to do this at 6. Right
36:39
Ronghui Gu: here. We declare map- mapping with this key value types and this mapping names balances.
36:45
Ronghui Gu: And then later, we can assess
36:52
Ronghui Gu: this mapping right using the key. Right
36:55
Ronghui Gu: practice, right
36:59
Ronghui Gu: excessive is, is similar to excessive array.
37:00
Ronghui Gu: Well, mappings are always stored in the storage range.
37:07
Ronghui Gu: especially if you are using mapping
37:12
Ronghui Gu: is stored on the
37:16
Ronghui Gu: per account sort, and it's very expensive, right
37:18
Ronghui Gu: at a
37:22
Ronghui Gu: and basically the the initially, you can do as well all the
37:24
Ronghui Gu: you give it any address. Right? It's default value is 0, right? But it's will now store the 0 on the storage right?
37:31
Ronghui Gu: The only stories when you
37:40
Ronghui Gu: update it right to a different volume. And then that's new value will be stored on the storage. Right? That's why for this. When you when you declare some storage, and if you are using the
37:43
Ronghui Gu: default, 0 volume, right is, the the cost is much lower, right when you write it to as if 1, 3, the different volume, right? You need to pay less, and later, when you set it back to 0,
37:55
Ronghui Gu: you will get some gas refund, because actually, you could free up some just free up some stocks space. I'm sorry.
38:10
Ronghui Gu: Okay, so then let's check some globally available variables. Right? We have seen this message before.
38:22
Ronghui Gu: Right? I'll see. Message message. The value means a waste or or users right carriage
38:30
Ronghui Gu: by this message, right? Trigger the smart contracts. Right?
38:37
Ronghui Gu: this signature doll, send dot data. This, this message about data is a call data
38:42
Ronghui Gu: message, dot data as a call. Even.
38:50
Ronghui Gu: okay? And also it says, Guest, left
38:53
Ronghui Gu: practice. Well, much like, yes, between that. And there's also
38:57
Ronghui Gu: this block is a global variable center.
39:02
Ronghui Gu: These are the
39:05
Ronghui Gu: the the functions right? Associated with this block, we have block hash.
39:07
Ronghui Gu: This is the current, the the we can go to the what is the coinbase.
39:13
Ronghui Gu: The 1st transaction is.
39:29
Ronghui Gu: go where
39:33
Ronghui Gu: the actually the dot coinbase in it is a minor
39:39
Ronghui Gu: right? And we have difficulties. Difficulties are blocked. Right gas limits
39:45
Ronghui Gu: number. This is your clock number
39:50
Ronghui Gu: right? And we have also the timestamp, the timestamp that is boss mind.
39:53
Ronghui Gu: And this is yes, this is kind of transaction. Right? Transition doll origin is origin
40:01
Ronghui Gu: address that started this transaction.
40:09
Ronghui Gu: Okay? And then we have Abi.
40:15
Ronghui Gu: right? So later, we'll show that as well kind of like this, avi, that you can see encode decode. This kind of stuff is used to, let's say, encodes the the function, signature, and arguments into a colleague.
40:18
Ronghui Gu: Right? The decode. We can deploy it.
40:35
Ronghui Gu: And we have this.
40:37
Ronghui Gu: Okay, calc, 256 is a hash function.
40:39
Ronghui Gu: Hash
40:43
Ronghui Gu: the data to to 30 bucks, right? Or 256 bits.
40:45
Ronghui Gu: and we have sharp, 256 sharp, 3. So on and up here there are also 2 special
40:50
Ronghui Gu: he will.
40:58
Ronghui Gu: globally available variables or functions, but it help require requires a semi call, sir.
41:00
Ronghui Gu: This is an example like require message style volume larger than 100.
41:08
Ronghui Gu: Otherwise trade insufficient files. Right?
41:14
Ronghui Gu: When we have this, when we have this function, this is at the ball, let's check. If the message of all is larger than 100 ways.
41:18
Ronghui Gu: if it's indeed the case, well, we can proceed, otherwise the content will will pause and print this error message that is insufficient, false.
41:27
Ronghui Gu: We're basically gonna use this kind of like require assert to
41:39
Ronghui Gu: add the chats into the smart contracts right to make it to to avoid some
41:45
Ronghui Gu: mistakes, or or avoid some kind of like
41:55
Ronghui Gu: unexpected imports. And so.
42:00
Ronghui Gu: okay, so then.
42:07
Ronghui Gu: we talk about function visibilities that we have briefly covered. When we define a function, we want to define the function visibility.
42:10
Ronghui Gu: right? We have covered public public means that the function can be called, both externally and internally
42:19
Ronghui Gu: right, an argument or copied from power data to memory
42:27
Ronghui Gu: right? And it says, well.
42:34
Ronghui Gu: the the arguments will be copied from colleague to the memory. So that's that's well, the you the. When we assess the arguments, we access the memory right?
42:37
Ronghui Gu: And here's a
42:49
Ronghui Gu: little bit different, one called external.
42:51
Ronghui Gu: The difference between external and public does external function can only be called from all side contract.
42:54
Ronghui Gu: That means as well, internal contacts
43:03
Ronghui Gu: function
43:07
Ronghui Gu: right? And here are. You must read your fake
43:09
Ronghui Gu: from copper.
43:12
Ronghui Gu: and the calling actually is cheaper than memory, right?
43:15
Ronghui Gu: So this is a temporary.
43:18
Ronghui Gu: And we call a function from actual contract. Purely. We.
43:20
Ronghui Gu: we, we we gotta encode this unless we can use address or caller, we can use address call. And then we pass a call data here, right? And which will pass up arguments. And then we'll we'll we'll be read by this function.
43:26
Ronghui Gu: and then we have private
43:44
Ronghui Gu: private means that's only visible to com functions within the current contract.
43:46
Ronghui Gu: Internal, it's different from
43:56
Ronghui Gu: private is that's not only be visible to the current contract, but also visible to the contest deriving from it.
43:58
Ronghui Gu: That's internal.
44:08
Ronghui Gu: Then. So the the
44:10
Ronghui Gu: the 1st 4 basically find function as a business right? The last 2 defines kind of like the memory view. Right? When we add a view, keyword makes us
44:13
Ronghui Gu: this function only read, storage, no rights to storage
44:23
Ronghui Gu: bye
44:28
Ronghui Gu: with a different. Another keyword upshore
44:29
Ronghui Gu: means that the function does not touch storage at all.
44:33
Ronghui Gu: There's no touch story there at all
44:37
Ronghui Gu: any questions so far.
44:42
Ronghui Gu: Go ahead.
44:46
Ronghui Gu: Super
44:47
Ronghui Gu: viewing.
44:48
Ronghui Gu: Hmm, differences. Sure, that's I'm sorry. Does not touch means that it will not even read. Yeah.
44:49
Ronghui Gu: yeah, sure, that's all touch, that's all. Read. That's all right.
45:02
Ronghui Gu: View me as we were really sorry. But we're not right. So sorry
45:07
Ronghui Gu: any other questions.
45:14
Ronghui Gu: Okay, so this is an example of function, definition, right or function. F,
45:20
Ronghui Gu: that's up
45:26
Ronghui Gu: arguments. You, you. I'm sorry it's you. Int, a, as a private function means that it's only visible to the this. The functions within the same contract and secure function means that does not touch storage. Right. The returns value is also is, is you eat? B,
45:27
Ronghui Gu: okay, here the function body is, return a plus one.
45:47
Ronghui Gu: Right?
45:52
Ronghui Gu: It reads, A, Y is still a short function.
45:54
Ronghui Gu: We're this a store
46:06
Ronghui Gu: memory right?
46:12
Ronghui Gu: This A could be stored in memory. So it does not actually read the storage
46:14
Ronghui Gu: either stored in the memory or store in the stack or call data that's now stored in the storage. Right?
46:23
Ronghui Gu: So even if we read A, we didn't touch storage, that's if this A is a state variable and you return a plus one, then it can't be a profile.
46:30
Ronghui Gu: The compiler will apparently errors to do that.
46:40
Ronghui Gu: Okay.
46:47
Ronghui Gu: any questions so far
46:48
Ronghui Gu: move forward
46:54
Ronghui Gu: so then let's look at this safe mask
46:56
Ronghui Gu: contract.
46:59
Ronghui Gu: This is a library used by opens up our competitor.
47:02
Ronghui Gu: but but it's why they used to
47:07
Ronghui Gu: library
47:10
Ronghui Gu: like the Sigmas. They say it ran lots of functions to
47:12
Ronghui Gu: mess with it, right calculation, and so on, and add lots of requirements, and so on, making sure that while we save to
47:17
Ronghui Gu: to call right, basically, if if you are trying to do some like, add, please do not go. Do not try to add, you should save, add right, provided by library. And let's say, well, this save ad does
47:26
Ronghui Gu: specific as well. We'll add a 2
47:42
Ronghui Gu: images right? You int. 256 integers.
47:45
Ronghui Gu: And it's an internal function
47:48
Ronghui Gu: means that it can be called by
47:51
Ronghui Gu: the function with this contract and the the contract in Harrison, right?
47:54
Ronghui Gu: And as a pure function mean that does not touch storage.
47:59
Ronghui Gu: right? And it returns you in 256 c. Okay. Here, C equals to A plus B. We can see that we
48:02
Ronghui Gu: we didn't need to do return. See? Right? Because
48:11
Ronghui Gu: the reason why we have R&D,
48:14
Ronghui Gu: the the return of variable right is at this time has already been
48:16
Ronghui Gu: declare right here.
48:21
Ronghui Gu: right? Okay. And we do C equals to a plus B,
48:22
Ronghui Gu: if we just see because it it's part B, right? Well, we don't need to have this function right?
48:27
Ronghui Gu: The the cool thing about the same app function is it added requirements. Seeing us
48:33
Ronghui Gu: C. Must be larger and equal to a
48:40
Ronghui Gu: otherwise, if you
48:44
Ronghui Gu: interested or for error.
48:47
Ronghui Gu: but actually it checks whether this
48:52
Ronghui Gu: additional will will cost for overflow in your overflow.
48:55
Ronghui Gu: Bye.
48:59
Ronghui Gu: although you in 256, a pretty large integer. But right we may still
49:02
Ronghui Gu: cause overflow right, though. That may be dangerous. That may be unexpected.
49:10
Ronghui Gu: Okay, so soon we'll have this contract. I'll say math.
49:17
Ronghui Gu: and we can implement a contract that in Harris the state Mass. And the keyword is, as IS. Right.
49:22
Ronghui Gu: we can use secure eyes to inherit the content, but assume a
49:29
Ronghui Gu: contract. A harrises same as contract.
49:34
Ronghui Gu: and the census function is internal.
49:37
Ronghui Gu: Right? So we have says this save add function. We can do something like you. Inch 256 a equals to save Ad. BC.
49:40
Ronghui Gu: What can I call this save
49:49
Ronghui Gu: add function right? And when and then, during kind of like, during the compilation. The safe mass code will be compiled into this contract A, and then later ask you, right? This is contract inheritance.
49:51
Ronghui Gu: Well.
50:07
Ronghui Gu: and sorry. They also support imports library imports.
50:10
Ronghui Gu: Now I can make it
50:14
Ronghui Gu: make make it easier like we can define seamless as a library.
50:17
Ronghui Gu: Right? Then the contract a can do something using save match for you. Inch
50:22
Ronghui Gu: 256.
50:28
Ronghui Gu: Many of us for any
50:30
Ronghui Gu: simple data type, for any variable has this type simple data type U into 1036.
50:33
Ronghui Gu: Actually, you can call the
50:39
Ronghui Gu: functions defined in the safe math library
50:42
Ronghui Gu: like this U inch, 256, a equals to b dot, c sc.
50:46
Ronghui Gu: right? We say, using Cms for you into 256 cataly.
50:53
Ronghui Gu: right? Right? Kind of like the when we do b dot, c, add, it's kind of like we call save add, the 1st argument is a speed. Well, second argument is a C,
50:58
Ronghui Gu: this is basically how we use it. Nice library.
51:14
Ronghui Gu: and when you call audit, and if you do add without using seamless style, save as we will give you a warning to your smart contracts.
51:18
Ronghui Gu: bye?
51:31
Ronghui Gu: And then
51:32
Ronghui Gu: let's with this language features right? We can define some something what we call a token smart contracts right, and it's functionality is to well define the the the business of mapping, right of token.
51:35
Ronghui Gu: of mapping contents. The balances of this token on each address right mapping and implement some functions like a main token, right? Transfer, token and stuff like that. Right?
51:53
Ronghui Gu: That's the
52:06
Ronghui Gu: I will say, the 1st
52:07
Ronghui Gu: very popular application
52:10
Ronghui Gu: build on top of Israel. Right? You can easily write such a small contrast to to issue and and keep track of and transfer tokens right. And that's initiate something what we call Ico, right? And I'm not sure if. And you have heard about it right? The initial coin offer right
52:13
Ronghui Gu: initial coin offered, and very popular in the year of 2017 right?
52:36
Ronghui Gu: And lots of people, lots of purchase issue. This kind of tokens upon Israel, and the standard template
52:42
Ronghui Gu: right to write such kind of like token smart contracts is called Erc. 20,
52:51
Ronghui Gu: and it's a standard Api for forgeable token right in contrast with nft, right? Not tokens right? Nft
52:57
Ronghui Gu: standard as well. Yes. Erc
53:05
Ronghui Gu: 71. And it's a standard Api for affordable tokens that provides basic functionality to transfer tokens or allow the token to be spanned by a 3rd party.
53:09
Ronghui Gu: You can even give the 3rd party the permission to spare some amount of your tokens.
53:21
Ronghui Gu: And
53:27
Ronghui Gu: it is a is a smart contract, a standard, smart contracts and mentions all user balances, meaning that it has a mapping right from address to
53:30
Ronghui Gu: the number of tokens
53:41
Ronghui Gu: number of tokens that holds by this address.
53:42
Ronghui Gu: And
53:46
Ronghui Gu: it's here the visibility is internal.
53:47
Ronghui Gu: Mesas is
53:51
Ronghui Gu: can only be read by the function in this context or contacts derived from it.
53:54
Ronghui Gu: Oh, and
54:01
Ronghui Gu: so it's a standard interface of all other kind of interrupt right with every student token
54:04
Ronghui Gu: right? Basically, we use this crc plan token, using this template using standard template. And the other
54:09
Ronghui Gu: contrast right?
54:16
Ronghui Gu: Have, even if you you implement some kind of like more functions, you have to implement more. But things that has this standard interface, right can be interacted with many other
54:17
Ronghui Gu: smart contract. So, for example, like
54:31
Ronghui Gu: later in in the next lecture, we'll talk about the desk right right then. If it's your team handle can be used by most of the desk.
54:34
Ronghui Gu: and no need for special logic for each talk.
54:45
Ronghui Gu: It's kind of like it defines this logic interface for this bundle.
54:49
Ronghui Gu: Okay? So here is,
54:53
Ronghui Gu: yes, token interface.
54:56
Ronghui Gu: Okay, it defines a transfer function.
54:59
Ronghui Gu: Right? Transfer.
55:04
Ronghui Gu: The basically.
55:07
Ronghui Gu: this is true address, right? This is value, basically transfer some amount of token to this address right to the app to the address, you know. 1st argument, right?
55:09
Ronghui Gu: As external
55:22
Ronghui Gu: function means, I can be called by
55:24
Ronghui Gu: public right? Okay, we have transfer from. So the 1st transfer
55:27
Ronghui Gu: currently kind of transfer from your
55:33
Ronghui Gu: own address, right from your own accounts. Well, the transfer from can be clear that you can transfer from a different address. But you need to provide the permission, right? You have to demonstrate that you have the
55:36
Ronghui Gu: authentication right to do this transfer.
55:50
Ronghui Gu: and then we have approved
55:54
Ronghui Gu: means that you can approve
55:56
Ronghui Gu: some address, some spanner
55:59
Ronghui Gu: to
56:02
Ronghui Gu: spend some the the value amount of tokens on your own address
56:04
Ronghui Gu: Tella, you grant some approval to the spanner
56:10
Ronghui Gu: right? Allow them to spend some, some amount of some amount of tokens on your account. Right?
56:14
Ronghui Gu: The total supply
56:21
Ronghui Gu: here because it's a read only function.
56:24
Ronghui Gu: Post supply will only
56:27
Ronghui Gu: kind of like, read the total supply. They sold it.
56:28
Ronghui Gu: And that is so
56:32
Ronghui Gu: is gotta read it about us
56:34
Ronghui Gu: of this, the owner's address.
56:39
Ronghui Gu: right? It's an external function. It's a view function, right? It's also real.
56:41
Ronghui Gu: right? The good. Here you can see the good, the good part of this view. Keyword. Right? We have this function. Check the balance. You
56:47
Ronghui Gu: you are sure that's well. This function will now change the medicine.
56:57
Ronghui Gu: It will only read Bounce.
57:01
Ronghui Gu: the last one. I call it a laws. The laws will check that. How much token
57:04
Ronghui Gu: has been approved by the owner.
57:11
Ronghui Gu: That's the spanner can stand right.
57:15
Ronghui Gu: they say, when you say, Well, approve as this spanner 10, then you can use this along as a check. That's well. The owner and the spanner. How much is a lot right
57:17
Ronghui Gu: to spam by the spam from the owner's account? Right? It should return 10
57:30
Ronghui Gu: any questions for this crc, vanity token interface.
57:39
Ronghui Gu: Okay? So let's say, the internal implementation back to see how? Erc, 20 token.
57:47
Ronghui Gu: implement the transfer
57:56
Ronghui Gu: fun function. Okay? So this is a company. Rc, 20. Token here is, this is
57:59
Ronghui Gu: keyword is inheritable is for inherits right? Inheritance. Right? This is token in Harris's. I erc training token because I basically defines the interface right? Or, you see, kind of
58:05
Ronghui Gu: okay. And it has a mapping
58:20
Ronghui Gu: right from address to you into 236
58:23
Ronghui Gu: this visibility is internal right balance they keep track of for each address. What is a token? Balance? Right?
58:27
Ronghui Gu: And and we define a transfer function.
58:36
Ronghui Gu: This is a 2 address, 2 addresses
58:40
Ronghui Gu: the address the the center wanna set.
58:44
Ronghui Gu: and the value is how much tokens one set.
58:50
Ronghui Gu: Okay? So at the at the beginning of 2 checks.
58:55
Ronghui Gu: the 1st check required that balances message dial center larger and go to volume.
58:59
Ronghui Gu: But basically.
59:06
Ronghui Gu: given the message that I'll send her
59:08
Ronghui Gu: right.
59:11
Ronghui Gu: he's a owner, right of the the
59:12
Ronghui Gu: the current accounts. We need to check the its balance to make to make sure that its balance is larger and equal to volume.
59:16
Ronghui Gu: Otherwise Michael's sad.
59:25
Ronghui Gu: so semantic homes, and
59:28
Ronghui Gu: and the second check is balance 2 plus value is larger and equal to 1, 2.
59:33
Ronghui Gu: As soon as we save add, that's a right.
59:39
Ronghui Gu: A, the A plus B should not equal to B something like that, making sure there's no
59:42
Ronghui Gu: it is a whole.
59:48
Ronghui Gu: Alright, then what it? What it does is for messages. All standard
59:50
Ronghui Gu: is where we're gonna
59:57
Ronghui Gu: oh.
59:59
Ronghui Gu: reduce as far as 5.
1:00:00
Ronghui Gu: And then for the 2 address 2, we're gonna increase its status by about
1:00:04
Ronghui Gu: right. You can see there's really no something like a sense of right. There's no message tapping right or point passing. It's just that we
1:00:10
Ronghui Gu: we opted about us
1:00:22
Ronghui Gu: kind of like we update the the- the ledger. Right? I think
1:00:24
Ronghui Gu: right. And this image is, we. We log the events and then return true.
1:00:31
Ronghui Gu: Go ahead.
1:00:36
Ronghui Gu: should we just transferred?
1:00:39
Ronghui Gu: If you have?
1:00:42
Ronghui Gu: Yeah, yeah, here, let's say we have a message of standard.
1:00:46
Ronghui Gu: right?
1:00:51
Ronghui Gu: So
1:00:52
Ronghui Gu: here, when you, when you transfer, means as well, we. The transfer from the the from address is message call center.
1:00:54
Ronghui Gu: basically the the address that's just
1:01:04
Ronghui Gu: send a message to to to. That's that's that evoked this smart contract
1:01:07
Ronghui Gu: right? If you do not have fraud address mean that by default we use a senders met the senders address.
1:01:16
Ronghui Gu: If you scroll from you needed to.
1:01:24
Ronghui Gu: You know you can pass the address right? But then, later, we need to check the sales
1:01:27
Ronghui Gu: package.
1:01:33
Ronghui Gu: Right? So this is the this is the most simple function. Right assembly
1:01:36
Ronghui Gu: out there the balances right, we reduce the message of senders.
1:01:41
Ronghui Gu: balance by volume, increase to
1:01:45
Ronghui Gu: address status
1:01:48
Ronghui Gu: by volume.
1:01:51
Ronghui Gu: Right? We're gonna see this.
1:01:52
Ronghui Gu: If we do not have the 1st check. What gonna happen
1:01:54
Ronghui Gu: if we do not have the
1:02:02
Ronghui Gu: 1st 1st check? Right? Let's say you only have.
1:02:05
Ronghui Gu: let's say you only have 10 tokens. You want to send credit tokens right? Because if we do not have a 1st check.
1:02:11
Ronghui Gu: then the this line balances 2 plus equal to volume.
1:02:18
Ronghui Gu: Bye.
1:02:23
Ronghui Gu: the the receiver will receive training, and that's a 10 tokens right?
1:02:24
Ronghui Gu: Even if you do not have enough tokens right? The receiver can still receive the the let's say, time tokens right? That will that will. That will be definitely
1:02:29
Ronghui Gu: expected right and should be avoided. And so that's why we the 1st
1:02:39
Ronghui Gu: we need the 1st require, and if let's say.
1:02:45
Ronghui Gu: if we do not have a second required.
1:02:50
Ronghui Gu: there may be overflow right for balance balances to plus equal to volume right? And the the true status may even be decreased
1:02:53
Ronghui Gu: by your by your behavior.
1:03:05
Ronghui Gu: Right?
1:03:08
Ronghui Gu: Okay? So this is a implementation for this transfer function for esc training.
1:03:10
Ronghui Gu: So you can see that actually, this information is not that complex
1:03:15
Ronghui Gu: right? But it's back to the year 2017
1:03:20
Ronghui Gu: it. So there are many, many projects that only have this crc, 10 token and the base kind of millions of dollars.
1:03:24
Ronghui Gu: That's what happened in Europe. 2017, right.
1:03:33
Ronghui Gu: the good old days.
1:03:38
Ronghui Gu: Okay? So then we're gonna talk also, Abi encoding and decoding.
1:03:43
Ronghui Gu: So for each function for each function in the smart contracts. So every function has a 4 by selector that is calculated as a 1st 4 buys of the hash of the function signature.
1:03:50
Ronghui Gu: So in a, for example, like the transfer function in a small context, looks like this. Right?
1:04:07
Ronghui Gu: So we've gone up.
1:04:14
Ronghui Gu: We gotta have a selector
1:04:16
Ronghui Gu: for this function.
1:04:19
Ronghui Gu: which is 4 Byte. Right? What do we do? Is we do 256
1:04:21
Ronghui Gu: transfer address you either. This is the signature of the function, right? We're gonna hash it to 256 bits, 32 price, and then
1:04:26
Ronghui Gu: only record the 1st 4 Byte
1:04:38
Ronghui Gu: of the function right. This 1st 4 Byte of it is called seductor.
1:04:41
Ronghui Gu: And why we want to have this selected because we want to do absolute function, call right. We need to address our call. We need to provide call data.
1:04:48
Ronghui Gu: And in order to provide calling, you need to.
1:04:57
Ronghui Gu: you need to kind of like, provide a
1:05:02
Ronghui Gu: data is bias. Right? We, you need anything which is a function call right within the smart contract. So we we use 4 by so indicate a a function within a smart contract
1:05:06
Ronghui Gu: within a small context.
1:05:21
Ronghui Gu: Okay, sucks.
1:05:23
Ronghui Gu: Right? So then in the call data, you can use 4 Byte indication, which of the content you gotta call
1:05:28
Ronghui Gu: right? And actually, it's a it was
1:05:33
Ronghui Gu: You can see that as well
1:05:40
Ronghui Gu: when we do a hash for 32 Byte. It's very, very hard to get a hash collision
1:05:42
Ronghui Gu: right?
1:05:48
Ronghui Gu: But here, if we only pick the 1st 4 Byte
1:05:49
Ronghui Gu: right, you could say you could catalyze
1:05:53
Ronghui Gu: kind of get a get a
1:05:59
Ronghui Gu: hash collision here, and there's a pretty famous attack
1:06:02
Ronghui Gu: you have to utilize U- utilizing this trick.
1:06:06
Ronghui Gu: That is well.
1:06:11
Ronghui Gu: kind of like keep changing, let's say the function name.
1:06:13
Ronghui Gu: and and the arguments ties together which is a different function. But has the same selector.
1:06:17
Ronghui Gu: And these 2 functions have different permission.
1:06:27
Ronghui Gu: And basically, that's how the the attackers started the attack. So use this hash question.
1:06:31
Ronghui Gu: And well, but this is a design right? This is designed for solid
1:06:41
Ronghui Gu: and
1:06:47
Ronghui Gu: then when we so when we pro let's say we have this selector right? And then the function, arguments will be encoded into a single byte array
1:06:49
Ronghui Gu: and the contaminated with a function sector. As a call data, right? We want to call data or call function
1:07:01
Ronghui Gu: with some articles absolutely right. You
1:07:08
Ronghui Gu: you basically encode the content arguments into a fire rate and concatenate it with a
1:07:12
Ronghui Gu: that's what I think
1:07:18
Ronghui Gu: a higher watch
1:07:20
Ronghui Gu: and so then.
1:07:23
Ronghui Gu: this is called call data, what will be sent to the address of the contract. And when we ask you is right, this call data will be decode
1:07:25
Ronghui Gu: to our, to the real arguments than than our actual.
1:07:35
Ronghui Gu: So that is how to
1:07:39
Ronghui Gu: to address our call right? We need to kind of like.
1:07:41
Ronghui Gu: construct this call data right? And then this call data will be decode decoded
1:07:46
Ronghui Gu: and then ask it
1:07:51
Ronghui Gu: from here. The address can be cost through contract types like we have a address like token.
1:07:57
Ronghui Gu: right? We can pass it to a contact.
1:08:05
Ronghui Gu: Given the address
1:08:10
Ronghui Gu: right, you can pass it this time from address to a token, and then
1:08:12
Ronghui Gu: you can. We can call the focus right that defined in this, in the, in the, in the contract.
1:08:18
Ronghui Gu: and when we. When we do this right, we we still kind of like. We only pass 2 value right as
1:08:27
Ronghui Gu: that's normally, but on the line as compiler, the solid compiler down the to the Api
1:08:34
Ronghui Gu: to contract accordingly.
1:08:42
Ronghui Gu: Alright and ask you
1:08:44
Ronghui Gu: any questions.
1:08:49
Ronghui Gu: Okay, then, well, gas cost right? So ev, right, everything costs gas.
1:08:54
Ronghui Gu: Okay? Because Evm, or either as a world computer, right? In order to draw some program on top of it, you need to pay gas for every single thing for every single session, right? Otherwise.
1:09:01
Ronghui Gu: the miners will now be motivated to run their program.
1:09:12
Ronghui Gu: Right? So you have to provide gas and
1:09:16
Ronghui Gu: including this edi decoding, including copy variables, memory, all this kind of stuff. Right? You have to pay everything
1:09:19
Ronghui Gu: right. Previously, we talk about how to kind of like, how to calculate gas right? Each interaction has some gas, and then you also need to kind of like propose your your gas price. All this kind of stuff right?
1:09:25
Ronghui Gu: And
1:09:39
Ronghui Gu: So in order to
1:09:40
Ronghui Gu: actually, early this year or late last year, the gas fee on Israel is very, very expensive.
1:09:42
Ronghui Gu: right? It's very private, and you have to. You want to pass optimization for your smart contracts
1:09:49
Ronghui Gu: right? And there are many factors you may want to consider as a developer like, how often do we expect certain functions to be called right? It will function will be called very frequently.
1:09:56
Ronghui Gu: we definitely
1:10:08
Ronghui Gu: you. We should try to optimize the best call as much as possible. Right? But also it's important as a cost of deploying the contract. All the cost, each individual function call
1:10:09
Ronghui Gu: right. Let's see, when we deploy the contract, we kind of initiate some state variables and state variables on on the storage right?
1:10:19
Ronghui Gu: And so last, one other variables been using call data, stack memory or storage
1:10:28
Ronghui Gu: call data will be passed
1:10:35
Ronghui Gu: right during the function call. And after you can refer to arguments right through call data.
1:10:38
Ronghui Gu: and you can also store the arguments as local variables on stack and also do it on memory or storage. Right?
1:10:44
Ronghui Gu: You want to determine which storage type you want to use for each channel.
1:10:52
Ronghui Gu: Okay? So 1st time is Stack
1:10:58
Ronghui Gu: Stash.
1:11:02
Ronghui Gu: He's not a so
1:11:03
Ronghui Gu: is stacked on either or anything else
1:11:05
Ronghui Gu: is- is stacked this-, this service type located on either blockchain or not.
1:11:13
Ronghui Gu: So
1:11:23
Ronghui Gu: basically, if you simply read the blockchain data, can you read the the stack overflow?
1:11:24
Ronghui Gu: No is now stored on blockchain
1:11:33
Ronghui Gu: it now. So it's not stored on, either. It's stored. It's stored where?
1:11:36
Ronghui Gu: Hmm!
1:11:45
Ronghui Gu: In the contracts.
1:11:46
Ronghui Gu: and as I guess you know where this stack is located.
1:11:47
Ronghui Gu: Yeah, miners machine, yeah, great, it's it's in Evm, right? But actually, it's located on miners machine, right? So basically with miners. Ask you this.
1:11:53
Ronghui Gu: the program that in the block? Right? So actually, it's this on minor stack. That's why we pay for using their machine storage. Right? It's on miners machine.
1:12:03
Ronghui Gu: It's not. He's a blockchain, he's a blockchain. It's kind of like what it's just a
1:12:16
Ronghui Gu: why.
1:12:21
Ronghui Gu: a pad only in Arabia
1:12:23
Ronghui Gu: even Blockchain is just a pen. Oh, a pen only didn't ring right, and
1:12:26
Ronghui Gu: that does not include sec barrels. But you can read the story barrels from this.
1:12:32
Ronghui Gu: A panel waiting in a room.
1:12:41
Ronghui Gu: That's why it's expensive. Thank you.
1:12:43
Ronghui Gu: Basically, that the set variables will not be. Actually, there's no space on the blockchain itself to store. The staff server is located on miner's machine.
1:12:45
Ronghui Gu: on medicine.
1:12:56
Ronghui Gu: Okay? And it can be used for any simple types that is less than equal to 32 Byte.
1:12:58
Ronghui Gu: Yes.
1:13:06
Ronghui Gu: and
1:13:09
Ronghui Gu: like you. Int 256, a goes to 201.
1:13:11
Ronghui Gu: Sorry. Okay, this is a
1:13:15
Ronghui Gu: less less than go to circle bypass. It can be located on stack.
1:13:17
Ronghui Gu: So basically have this local variable. That is a local variable. U 8. This is a equals 523
1:13:22
Ronghui Gu: by default. It's located on stack.
1:13:30
Ronghui Gu: Unless right, you add a keyword like memory salary, then it will not be
1:13:33
Ronghui Gu: okay. I'll say, Okay, there, there's only 1,024 set variable flaws
1:13:38
Ronghui Gu: makes sense right?
1:13:45
Ronghui Gu: You you can't. You can't reserve a a very huge sorry on my desk machine. Right.
1:13:47
Ronghui Gu: Let's say we only reserve 1,024, 7 h.
1:13:53
Ronghui Gu: and each slot can hold 32 MB
1:13:58
Ronghui Gu: right? Each slot
1:14:04
Ronghui Gu: size a certain parts.
1:14:06
Ronghui Gu: and actually on E as Edm level, all simple types are represented as by solution.
1:14:12
Ronghui Gu: and it can be sort of set. So that's it. Statics
1:14:19
Ronghui Gu: almost achieve this
1:14:24
Ronghui Gu: right? So call data is also better. Cheap. Right? Stag is better cheap.
1:14:26
Ronghui Gu: Why? Because
1:14:30
Ronghui Gu: you don't. You don't put it on the blockchain. Only business on miner's machine.
1:14:31
Ronghui Gu: Okay.
1:14:36
Ronghui Gu: the call data call data is a rate only by an array. Right? When we call function. Right? We contract this call data right? And each byte of a transaction call data costs gas.
1:14:38
Ronghui Gu: 68 guests per nonzero byte, 4 guests per 0 Byte. You guys see, 0 Byte is very cheap.
1:14:50
Ronghui Gu: right? Very cheap. But it's not for free. Right?
1:14:58
Ronghui Gu: It's just forecast. Non. 0 bias on
1:15:02
Ronghui Gu: call data is 68 guests. Okay, it's cheaper to load variables right from call data rather than copy them to memory. Right?
1:15:06
Ronghui Gu: Let's see, kind of like you have. We have to set it from message dot data, right, we very assess it is
1:15:14
Ronghui Gu: cheaper than excessive memory.
1:15:20
Ronghui Gu: Right is. This can be accomplished by marketing a function as external when we market a function as as an external for a public function, if it not, will not be, that's say, a call by internal
1:15:26
Ronghui Gu: contracts. It can be a actual function. Call right for actual function calls the the
1:15:38
Ronghui Gu: colleague will not be
1:15:45
Ronghui Gu: copy to memory. Right?
1:15:47
Ronghui Gu: The memory. Memory is a binary and a complex task, like array charts that strings.
1:15:51
Ronghui Gu: These are larger than circle bias must be stored in the memory or in story. We can't store. This complex has in Sec
1:15:58
Ronghui Gu: bye.
1:16:08
Ronghui Gu: And, for example, the string memory name. It also adds right.
1:16:09
Ronghui Gu: But if we do not put memory here.
1:16:14
Ronghui Gu: it will still not be
1:16:17
Ronghui Gu: puts into stack right? Good because it's complex.
1:16:19
Ronghui Gu: It's a complex article, right?
1:16:24
Ronghui Gu: But well, that's it. We can eat. Memory
1:16:26
Ronghui Gu: name equals 5. Something like that. Right?
1:16:30
Ronghui Gu: Various keywords that explicitly.
1:16:33
Ronghui Gu: Say that. Well, this variable is located in a memory marriage tree.
1:16:37
Ronghui Gu: but not as cheap as that. There's much cheaper than storage, but the cost of memory grows quadropically right.
1:16:42
Ronghui Gu: So again.
1:16:49
Ronghui Gu: you did a lot of spam also. No.
1:16:50
Ronghui Gu: So last one I started right very, I guess, where this memory is located
1:16:54
Ronghui Gu: on the blockchain or on the miners machine or somewhere else.
1:17:00
Ronghui Gu: Machine minus machine.
1:17:10
Ronghui Gu: Sorry, Silas.
1:17:12
Ronghui Gu: Okay. And
1:17:16
Ronghui Gu: the storage right? Storage is very expensive, because storage will be
1:17:18
Ronghui Gu: located on the blockchain.
1:17:24
Ronghui Gu: and we'll be always there right. We'll pull something in a storage.
1:17:28
Ronghui Gu: It will always will always be there. It can be, can be visible to the rest of the world.
1:17:33
Ronghui Gu: and branding 2 is very is most expensive, really, from it is cheaper
1:17:39
Ronghui Gu: right? And mappings and stables are always installed right.
1:17:45
Ronghui Gu: The guitar mapping, so dependency variables are always in storage. So
1:17:50
Ronghui Gu: is it a function right? If you declare a mappings
1:17:54
Ronghui Gu: just want to use it locally, but it should be helpful. Right?
1:17:58
Ronghui Gu: It's very expensive. And some guys, they respond with storage delayed or set to 0. Right?
1:18:02
Ronghui Gu: So there are some tricks for saving gas for some variables you need to store into the storage whose size less than 30 Byte, we can compact them into 32 by slots.
1:18:11
Ronghui Gu: Then there's another way called event loss. Right?
1:18:28
Ronghui Gu: Basically, downloads are cheap way of storing data that does not need to be accessed by any context. So will you
1:18:31
Ronghui Gu: log? Something right is will also be reported on launching.
1:18:38
Ronghui Gu: like, for example, previously, when we transfer some data or we can, we can log log right everything. We ran to the domain name. We can log it.
1:18:44
Ronghui Gu: It will be stored on the blockchain, but it's cheaper than storage, because
1:18:53
Ronghui Gu: assume it will not be read by any other small context, right? Only if you read like by some human beings or some other applications, right? That we raised from Boston data, right? So it's cheaper.
1:18:57
Ronghui Gu: but it's not stored in. The storage is stored in the transaction receipts.
1:19:10
Ronghui Gu: We we call it
1:19:16
Ronghui Gu: okay. The last thing is about cyber security. Right? I think the security issues we need to consider. So
1:19:20
Ronghui Gu: for for example, like, are we checking mass calculations for overflows and other flows? Right? That's why, please use it? Mass, library, right? And what a search that should be made about function improves regional values and a contrast stage.
1:19:30
Ronghui Gu: You can see smart contracts quite different from regular program because they're gonna run on world computer
1:19:44
Ronghui Gu: really will manage a huge amount of asset. Right? So
1:19:51
Ronghui Gu: is you need to be really careful right? You want to add lots of assertions. So making sure that bad things will not happen right.
1:19:56
Ronghui Gu: and the who is a large corporation, this is very important. Right? Like you have smart contract. You have function called the meet
1:20:04
Ronghui Gu: mean right, the mean tokens. And you said the permanent Republic. They made it right.
1:20:12
Ronghui Gu: The the menu will mean the tokens and their tokens price will drop to. There it happened
1:20:17
Ronghui Gu: this kind of thing could happen.
1:20:24
Ronghui Gu: And the
1:20:27
Ronghui Gu: are we making any assumptions about the functionality of external contracts that are being called
1:20:28
Ronghui Gu: right? This is also important, right?
1:20:34
Ronghui Gu: So
1:20:37
Ronghui Gu: sometimes you call a small contest right? We may have some
1:20:40
Ronghui Gu: assumption, and whether this assumption
1:20:44
Ronghui Gu: hold on out
1:20:47
Ronghui Gu: bye.
1:20:50
Ronghui Gu: okay? And
1:20:51
Ronghui Gu: then I see a reentrance re-enturcing park after the most famous one called the doll attack
1:20:53
Ronghui Gu: right? Haven't done the yield training
1:21:00
Ronghui Gu: 60.
1:21:02
Ronghui Gu: And on this the ball contest this count has implemented.
1:21:03
Ronghui Gu: It's kind of like a bank contracts, and everyone can deposit your token there
1:21:08
Ronghui Gu: and then later, number 12, right? We can use this
1:21:13
Ronghui Gu: bank accounts to to do some investment, and so on. Right. This is A.
1:21:16
Ronghui Gu: This contract called The Doll, and there's a very famous attack on this contract called the Doll Attack, I mean in 2016, and at least 2 more than 3 million, the loss of 3 million users
1:21:21
Ronghui Gu: through Miller.
1:21:34
Ronghui Gu: Jesus. Bye.
1:21:35
Ronghui Gu: it's kind of like. Consider. It's been considered as a largest cyber attack in history, but also this is the fog of Israel, right to Israel and the Israel classic.
1:21:37
Ronghui Gu: These are classic means as well.
1:21:50
Ronghui Gu: We are in the disintization world. Right? We need to respect code as well. Right? Your code has vulnerabilities. So what right? So we need we, we still want to respect it. But that's easier on task, and the kind of means. Well, well, we don't want to admit this this hack. We don't want to make this mistake. Let's do a hard fork before this attack. And basically kind of like, you can see, it's a harmful at that time
1:21:52
Ronghui Gu: either using the pow process right? Means all the miners should try to mine.
1:22:19
Ronghui Gu: to the, to the append your block to the longest chain. Right?
1:22:27
Ronghui Gu: But internal foundation, Vitalik. Obviously. Well, that's- that's
1:22:31
Ronghui Gu: there is a call, all the miners who work not on the long, long chain, but on the specific.
1:22:35
Ronghui Gu: the the chat. That's a regret. This mistake I fixed this, and a
1:22:41
Ronghui Gu: of course, later that should become longer right. But the reason why, there's still a large group of people blowing isn't classic because they feel like, well, you know, that's something like
1:22:46
Ronghui Gu: betray the spirit right of blockchain betray the spirit of civilization.
1:23:00
Ronghui Gu: But I would say definitely, right decision.
1:23:05
Ronghui Gu: Look at the current developments of user right? And these are classic. Of course, you know, user is much, much more successful, and also by denying such kind of big loss right then. Most users are still controlled by the original owners. Right? So it has this volume so
1:23:09
Ronghui Gu: well, whatever we'll not debate on this point. But let's look at this contract and see
1:23:24
Ronghui Gu: what happened. Like, why.
1:23:30
Ronghui Gu: it leads to such big attack. Right? So first, st is a contact back. Right?
1:23:32
Ronghui Gu: You.
1:23:38
Ronghui Gu: okay, so this is contract back. It has a a valid user balances, which is mapping from address to you. Int.
1:23:39
Ronghui Gu: Right? You eat the same as using 256. Okay, it has one function called the get a user balance. Right? It's straightforward right return to user balance. Add to balance, basically gonna add a message about you
1:23:48
Ronghui Gu: to the user balance. Of course, it's simplified version, right? We need to check the overflow. But let's ignore it.
1:24:04
Ronghui Gu: It's not a issue here. The issue is about this, 1st robots
1:24:10
Ronghui Gu: withdraw bonuses. As the this one has tried to withdraw all the remaining files of your account.
1:24:15
Ronghui Gu: Okay, so what it does
1:24:23
Ronghui Gu: is given the message of center right.
1:24:26
Ronghui Gu: which is one that initiated this call. Right?
1:24:30
Ronghui Gu: Let's use its address, which has a user balance and put it to a module.
1:24:34
Ronghui Gu: Okay.
1:24:40
Ronghui Gu: forget about us
1:24:41
Ronghui Gu: of the the centers account. Right? We have the best.
1:24:43
Ronghui Gu: and then we check that. Then we send a false caller.
1:24:46
Ronghui Gu: we set a false
1:24:52
Ronghui Gu: equal to amount to withdraw
1:24:54
Ronghui Gu: right here. It's message call center, which is address. Right
1:24:59
Ronghui Gu: thoughts
1:25:03
Ronghui Gu: call.
1:25:05
Ronghui Gu: This call should be
1:25:07
Ronghui Gu: function to send
1:25:09
Ronghui Gu: to send to basically send the token right with the volume
1:25:12
Ronghui Gu: does equal to amount to withdraw.
1:25:18
Ronghui Gu: If it's equal to false means that well, this function failed.
1:25:21
Ronghui Gu: Throw. It's kind of like a boss right? And revert this back. Revert all the States back.
1:25:25
Ronghui Gu: This is important. The-the- the developer. See that? Well, if something bad happened, I will revert it back. Right? Okay, added, it
1:25:32
Ronghui Gu: says, user bus equal to 0.
1:25:40
Ronghui Gu: This is something like, well, we 1st get a, we get the account withdraw like your your account has 10 users, let's say, or 10 way. Okay, we get this 10, and then we try to send this 10,
1:25:43
Ronghui Gu: and if it's if it's fail, we can reverse this back. If we succeed
1:25:58
Ronghui Gu: well, we send the pattern should be 0.
1:26:04
Ronghui Gu: Bye.
1:26:11
Ronghui Gu: What's the issue of it.
1:26:15
Ronghui Gu: The issue is here. So it's called the reentrancing of that attack needs as well. You can see this withdrawal as is public. Okay? Right?
1:26:24
Ronghui Gu: Let's say if we, if if someone has 10 week in his amount in his account and a call is withdrawal, balance
1:26:34
Ronghui Gu: right and
1:26:43
Ronghui Gu: well, this function, get the balance and send the money to him.
1:26:45
Ronghui Gu: Assume is wrong in parallel.
1:26:50
Ronghui Gu: and you can call again
1:26:54
Ronghui Gu: right before the balance we reset to 0. We can call it in parallel. And the way this withdrawal balance function is called.
1:26:56
Ronghui Gu: you will get the balance which is out there. So that's a 10 way. Right then. Here we send the 10 way to the
1:27:05
Ronghui Gu: to the to the center, right? It's kind of like.
1:27:12
Ronghui Gu: But for this value is set to 0. If this function can be called multiple times.
1:27:18
Ronghui Gu: In parallel you can definitely spend. You can get much more money
1:27:24
Ronghui Gu: then. My, you own other account right?
1:27:28
Ronghui Gu: But of course, Israel does not allow parallel execution, right? But you can think about this problem right? If we can call this in parallel.
1:27:31
Ronghui Gu: it's definitely very generous, right?
1:27:40
Ronghui Gu: So before this user balance is set to be 0.
1:27:42
Ronghui Gu: Therefore this user balance is set to be 0.
1:27:47
Ronghui Gu: whenever you call it you.
1:27:54
Ronghui Gu: the money you will receive. If you go to the poorest balance, right? You can call it multiple times. Right? You can.
1:27:57
Ronghui Gu: This is called double span tech, right? It's called double span tech, but either does not allow parallel exclusion.
1:28:03
Ronghui Gu: Right?
1:28:10
Ronghui Gu: So then, how does Tiger utilize this kind of like? More vulnerability?
1:28:11
Ronghui Gu: Yes.
1:28:19
Ronghui Gu: right.
1:28:20
Ronghui Gu: You're really running the gas
1:28:21
Ronghui Gu: to the call function. And it's emitted from the sender, in which it's
1:28:24
Ronghui Gu: yeah, very, actually very close with us. Actually, the the thing is, it's called right here. Send we you sender dot call right?
1:28:32
Ronghui Gu: You will assume that the sender, the, this is the actual phone call, right?
1:28:44
Ronghui Gu: This is a external function call. And this address our call right. We power, is at the beginning, right? Given the address, you have a call function that you can call this external function. And actually.
1:28:50
Ronghui Gu: but it's
1:29:03
Ronghui Gu: what's the assumption do you have
1:29:04
Ronghui Gu: for that external function
1:29:07
Ronghui Gu: actually here does not have the something right? And let's look at the
1:29:09
Ronghui Gu: send them.
1:29:17
Ronghui Gu: Now, this is a sender. This is a tech or smart contract. The center is a smart contracts, right? Interact with this bank contract, and for this sender
1:29:18
Ronghui Gu: well, you can see, is 1st of all, is has a
1:29:29
Ronghui Gu: number of iteration that has a bank. This bank is the the ball attack. This is a ball contact right? And here, what we do is this is a constructor.
1:29:33
Ronghui Gu: How sales are functioning.
1:29:44
Ronghui Gu: We do. We gonna use the bank address. This is the address that this content deployed right to construct a bank contact, and we set a number of iteration to 10,
1:29:45
Ronghui Gu: and here we 1st add a 75
1:29:59
Ronghui Gu: ways to the balance. Right? We deposit 75 ways to the, to the, to the
1:30:02
Ronghui Gu: balance right? And then what's wrong? Balance code to a false. Here we call back, always wrong.
1:30:08
Ronghui Gu: We call backlog withdrawal. So this attacker contract
1:30:15
Ronghui Gu: will
1:30:21
Ronghui Gu: 1st deposit 75 ways to his own account and then call virtual balance into it with his bank contract.
1:30:23
Ronghui Gu: And then here.
1:30:31
Ronghui Gu: what do you call withdrawal? Balance
1:30:34
Ronghui Gu: right instead of this amount, which also be 75. Wait right?
1:30:37
Ronghui Gu: And it's trying to do. Message dot sender, which is a address of this attacker contract, and it's dot call. Call this amount to withdraw.
1:30:41
Ronghui Gu: Assume that the contact should have a
1:30:53
Ronghui Gu: the address function handling this right. However.
1:30:57
Ronghui Gu: this is a type function
1:31:01
Ronghui Gu: do not have
1:31:03
Ronghui Gu: call. Do not have the corresponding call, and it has a full background is that when the address is called and there's no co- corresponding
1:31:05
Ronghui Gu: method being being matched, we'll go to this format option.
1:31:15
Ronghui Gu: So in a sentence, this message, I'll send it on call will trigger this fall back.
1:31:20
Ronghui Gu: And what this phone call back function does is
1:31:26
Ronghui Gu: basically
1:31:30
Ronghui Gu: if the number of iteration is larger than 0 number iteration to mass minus and then
1:31:31
Ronghui Gu: coldness. Right? It's okay
1:31:37
Ronghui Gu: in a sandals
1:31:39
Ronghui Gu: during this country. Call
1:31:40
Ronghui Gu: right? He said. Kind of like 7 this week
1:31:44
Ronghui Gu: before it's end, before the termination of this call
1:31:48
Ronghui Gu: is called withdraw best again. So kind of like. There are many, many levels of withdrawers.
1:31:53
Ronghui Gu: withdraw balance within call function. And to create this
1:32:02
Ronghui Gu: infinite iteration. Yeah, so it's kind of like, kind of like, turn this call as a recurre recursive function to this through this with robust
1:32:08
Ronghui Gu: function, right? And then every time it enters, the amount withdraw will always be 75 week, right.
1:32:17
Ronghui Gu: the the one on the balance sheet right? So keep doing it. And why? It has some numeration limits.
1:32:24
Ronghui Gu: because making sure running out of that's not running out of gas. Why, if it's running out of gas, it will return fault and it will slow. The State will be converted. So we're making sure that's why it will not run out of gas. And then
1:32:32
Ronghui Gu: but we'll call this as well. Call this
1:32:44
Ronghui Gu: multiple levels with the initial 75 ways right in advance, and then after that right, although in each.
1:32:47
Ronghui Gu: in each function call in the end the balance will be set to 0, set to 0 7 0 while
1:32:55
Ronghui Gu: that's a dog hack.
1:33:04
Ronghui Gu: Okay? So
1:33:08
Ronghui Gu: this is a vulnerable function. How to fix it?
1:33:10
Ronghui Gu: Any idea?
1:33:22
Ronghui Gu: Go ahead. New chat.
1:33:27
Ronghui Gu: the call output.
1:33:30
Ronghui Gu: It's a function call right? So well, we don't know sender, we'll write this country don't know center, right?
1:33:32
Ronghui Gu: So actually, the ideas.
1:33:44
Ronghui Gu: So actually.
1:33:53
Ronghui Gu: we can push this.
1:33:55
Ronghui Gu: should we send instruction before sending it?
1:33:58
Ronghui Gu: Yeah.
1:34:04
Ronghui Gu: right? So we use amount to withdraw to get the balance and then set the balance to be 0.
1:34:06
Ronghui Gu: And then, even if lawyers here
1:34:12
Ronghui Gu: call recursively.
1:34:15
Ronghui Gu: the balance is already set 0. This balance is on the storage right.
1:34:17
Ronghui Gu: This on the storage is only set to 0. Sorry. So even if you call it many times right, only the 1st time you can withdraw 75 way for the resting.
1:34:22
Ronghui Gu: Oh, that's wrong, like you. You will get this wrong here
1:34:35
Ronghui Gu: because it does, Army said to do.
1:34:39
Ronghui Gu: The next time you get you get into a job as object
1:34:42
Ronghui Gu: right. The amount withdraw is will be 0 right. Nothing will be withdraw from
1:34:46
Ronghui Gu: right. But the thing is here.
1:34:51
Ronghui Gu: When it fails right, we need to reset the best. But this one.
1:34:54
Ronghui Gu: That's how we can fix it
1:35:01
Ronghui Gu: bye.
1:35:03
Ronghui Gu: if the developer right in a different way, right at that time
1:35:07
Ronghui Gu: more than hundreds of dollars. I can say
1:35:11
Ronghui Gu: that that's 1 of the reason that inspires
1:35:16
Ronghui Gu: Major Star survey. But how do we improve the
1:35:20
Ronghui Gu: security of smart contracts?
1:35:24
Ronghui Gu: Okay.
1:35:27
Ronghui Gu: that's this. And then we can
1:35:28
Ronghui Gu: through the discussion section.
1:35:32
Ronghui Gu: But for all the thought
1:35:39
Ronghui Gu: before I started any any question from you.
1:35:42
Ronghui Gu: applause, star
1:35:45
Ronghui Gu: a startup or respond, and we have
1:35:47
Ronghui Gu: think of
1:35:51
Ronghui Gu: have have thought of raising funds.
1:35:52
Ronghui Gu: Something like that?
1:35:55
Ronghui Gu: Any questions?
1:36:04
Ronghui Gu: Okay, no questions. I will. Yeah, I will, perfectly.
1:36:06
Ronghui Gu: I'll briefly discuss how you need to do right? What? What's kind of like preparation you need to do to to start raising farm right? And actually many kind of like
1:36:13
Ronghui Gu: have asked me this kind of question, because from the public record, let's say we
1:36:30
Ronghui Gu: we did very successful fundraising in the past, right? Kind of like from 2021, 2022 in within 8 months. Right? We we finished 4 round of fundraising.
1:36:36
Ronghui Gu: And we've raised in total, about 230 million dollars. Something like that
1:36:47
Ronghui Gu: and is is to be honest, is is hard to do that, because usually it takes 3 to 6 months to finish a round of fundraising.
1:36:52
Ronghui Gu: So right as is is very abnormal, right to finish 4 runs within 8 months. I mean, that's well, we finish every single round within 2 months. That's not not a no normal case. Well,
1:37:02
Ronghui Gu: basically. Well, yearly, right? A run of fundraising takes about 3 to 6 months.
1:37:16
Ronghui Gu: and well,
1:37:22
Ronghui Gu: how to start right? So as I mentioned so there are different Rana, or different service of fundraising right? Starting from C,
1:37:25
Ronghui Gu: or even precede someone said, preced one and see one, and then series a service B series C, right? So as I mentioned, so c. 1 or precede one. You only need to have an idea. Have a team right?
1:37:36
Ronghui Gu: And series a, it's kind of you need to have a port time. You need to have clients. I need to have someone
1:37:47
Ronghui Gu: who is waiting to pay for your product. And later on. Basically, you have to demonstrate the product market fit, meaning that you have a significant amount of.
1:37:54
Ronghui Gu: let's say, clients, users, and so on. To demonstrate. Well, your thing can grow and scale. Right? That's everything. So let let's focus on c 1, right? Because I think that's more useful for all the students for c, 1
1:38:02
Ronghui Gu: as I mentioned, you basically only need
1:38:19
Ronghui Gu: idea, right? Company. Name right? The team. Idea. What do you wanna do right. And some slides, right? What do we call the the business plan?
1:38:24
Ronghui Gu: Right? Only need this thing to to to go to early stage investors or and annual investors, and try to get your 1st check right so for s. 1, as
1:38:35
Ronghui Gu: as I mentioned you, you try to use a safe right at as a FE. Right the simple agreements for future equity, right divided by a wine combinator. Use that template to to do a fundraising and then help start right? So who you should talk to? Right to raise funds? Right? So basically, there are also
1:38:49
Ronghui Gu: what we call the early stage Vcs
1:39:11
Ronghui Gu: and Android investors are famous android investors, and it sound like a X rater right programs like Y combinator right? And so on. So these are typical places. You can get your 1st check
1:39:13
Ronghui Gu: right? It's it's not that hard to get the
1:39:29
Ronghui Gu: contact information of this. We are, get my good question. So I got my 1st check. Actually, we will. I closely runs from several early stage Vcs, some annual investors, and so on. And for example.
1:39:32
Ronghui Gu: like
1:39:49
Ronghui Gu: that's funded by Professor Shu Ting Zhang.
1:39:52
Ronghui Gu: who is a former professor at Stanford University.
1:40:00
Ronghui Gu: Unfortunately, that's past week, you know we get a chat from them. We get a check from live speed.
1:40:04
Ronghui Gu: which is a very.
1:40:12
Ronghui Gu: I would say, pretty big, famous. CC, actually, they really do not participate in this kind of like. See one. The reason we can get money from it, because you know the article upon Shaw, who is my beauty advisor. Also the Computer Science Department chair at your university knows one of the big partner there. So we have some connection, right? So get some money from, and we also get money from finance.
1:40:15
Ronghui Gu: So Finance. Sorry it's the
1:40:39
Ronghui Gu: actually started the. It's investment arm, which is called finance labs in the year 2018. So after they invested us before they established the investment arm. So that is why our
1:40:42
Ronghui Gu: share table right? So while shareholders finance rather than finance labs. It introduces lots of troubles for us, because every single time we need to do something, or we need to add this. Some, let's say, some company rules somebody lost or or have new wrong reason. We need to get a signature from the holder of finance with
1:40:57
Ronghui Gu: right Cz. It's known as Cz, and it's purposely it's very, very hard to reach rich him. So every time we need to guess. Since his signature, we need to fit wait for several weeks. But a little later. Yeah, we can. Yeah. So later, I will say, for companies invested by finance labs. Right? Your, the the entity on your share table should be finance labs right? Then that's much easier.
1:41:20
Ronghui Gu: So we are kind of like, almost
1:41:46
Ronghui Gu: they're the 1st honey
1:41:49
Ronghui Gu: invested by by banners and
1:41:51
Ronghui Gu: get a check from them. We also get check from another angel investor right? Also. Pretty famous investor out there that we probably get it. And we
1:41:54
Ronghui Gu: raise our c 1. Actually, we'll only have a T
1:42:04
Ronghui Gu: idea and some business plan what we call so nothing. Yeah, back back to the point. I think we have about 10 people around 10 people and most of them, of course, part time engineers, right
1:42:08
Ronghui Gu: Google or Facebook, and so on, part time. And and 2 or something like that. So pretty small team. And it can be part time students, we can be part time license engineers and so on. It's it's it's okay.
1:42:24
Ronghui Gu: But what you need is a business plan, what we call business plan.
1:42:40
Ronghui Gu: And that's important. That's very, very important.
1:42:43
Ronghui Gu: Because I I think the most important thing I would say is your team's background.
1:42:47
Ronghui Gu: That's the most important thing. For example, if you are serious
1:42:52
Ronghui Gu: entrepreneur, right? You have
1:42:55
Ronghui Gu: build some company that's already got Ipo right? They start a new company. Yes, of course you can easily, with tons of fun or you're let's say, a senior director from Google, right? Working on, let's say, Google map. And you, wanna you wanna build a startup create the next generation of maps.
1:42:58
Ronghui Gu: Yeah, it's much easier for you to to to to respond.
1:43:16
Ronghui Gu: But let's say, if you're seeing here
1:43:21
Ronghui Gu: Director of Google for Google Maps, and I want to
1:43:23
Ronghui Gu: builder. Last name.
1:43:27
Ronghui Gu: a restaurant company.
1:43:29
Ronghui Gu: It will still be very hard
1:43:31
Ronghui Gu: for you to respond. Right? Basically.
1:43:33
Ronghui Gu: given your team's background and the idea right? The product you want to build.
1:43:36
Ronghui Gu: If people feel like well.
1:43:41
Ronghui Gu: you got a really, you really got a good chance to succeed right to successfully view the the this idea to implement your idea.
1:43:44
Ronghui Gu: then you get a very good chance to respond.
1:43:51
Ronghui Gu: So the team background is the most important thing.
1:43:55
Ronghui Gu: Oh.
1:43:57
Ronghui Gu: but for you, for you guys, right? You say, well, we're serious, right? One drop off. We don't recommend you to drop off, but that's it. We want to drop off.
1:43:58
Ronghui Gu: Is this a plus, or is it minus?
1:44:11
Ronghui Gu: So I will say that is, is not minus actual. So for early investors, very early investors for this annual investors. Actually they are looking for young, talented, passionate.
1:44:15
Ronghui Gu: At first, st
1:44:30
Ronghui Gu: so say, well, I'm a calling. Students have a great idea, right? And there's something like well, now
1:44:32
Ronghui Gu: is within my reach, right? I have a within my reach, and I have a group of
1:44:40
Ronghui Gu: other talented students. Well, actually, it's your way. It's not that hard for you to get a get your 1st check, and then what you need is very great business time.
1:44:49
Ronghui Gu: So what what is the business plan business plan. This is a few slides like a lecture slides right?
1:44:58
Ronghui Gu: You? Wanna
1:45:04
Ronghui Gu: how about 1st of all, what is your idea like? What do you want to do.
1:45:06
Ronghui Gu: and why you want to do it
1:45:10
Ronghui Gu: right? Why, sometimes it's more important than what and how. But
1:45:12
Ronghui Gu: as soon as I say that you still need to say what you want to do, because sometimes, if you fail to explain what you want to do right, that that of course, you will fail to find reason right? You need to explicitly, clearly state what exactly you want to do
1:45:16
Ronghui Gu: like for Elon Musk said, well, you wanna right. You. Wanna
1:45:30
Ronghui Gu: you want to travel to Mars right? Something like that, right? Very clear. Right? What do you want to do? And why you want to do it right? Because he feel like, well, it's a future for the human beings, right? Someone, someone needs to do it right. And it that someone will be him right. That's why. And
1:45:34
Ronghui Gu: These 2 parts. Very important.
1:45:51
Ronghui Gu: important.
1:45:54
Ronghui Gu: might say, well, it's important means that you you need to. Clearly you need to be clear what you want to do right like, for example, the slogan, something I want to secure the the web. 3 world or blockchain world. But what exactly we want to do right.
1:45:56
Ronghui Gu: Want to see that? Well, that's what we want to do. And completely right, something like we want to improve the security of smart contracts
1:46:12
Ronghui Gu: to to reduce the loss, and even to prevent all this kind of stuff, right? Something like that. You need to have maybe some bigger goal. But you want to help make it concrete, right? What? Exactly you want to do right? And second, why you want to do it.
1:46:20
Ronghui Gu: that's all that's important. What motivate you doing it
1:46:35
Ronghui Gu: right? What a motive is!
1:46:40
Ronghui Gu: So to this lecture, especially the last few slides you can see. Well, that's why I want to build 30.
1:46:41
Ronghui Gu: Right? Look at this very simple, smart contract. Right? Just one line mistake, at least. You
1:46:46
Ronghui Gu: hundreds of millions of dollars for financial loss. Right? And we can build something to prevent to prevent it right? And and how much value it is right
1:46:52
Ronghui Gu: like.
1:47:03
Ronghui Gu: So that's how important is you to to to do to do so. These 2 things, the 2, these 2 things is more like you need to make things clear.
1:47:04
Ronghui Gu: right?
1:47:15
Ronghui Gu: Right? Rather than something that nobody can understand. Right? Okay, the last step, how?
1:47:16
Ronghui Gu: But of course you don't know how.
1:47:21
Ronghui Gu: You don't know how to build a multi 1 million dollar was company right from the beginning. But this, how is something like, well, you want to show me you have the potential to be big.
1:47:24
Ronghui Gu: right? That is
1:47:35
Ronghui Gu: like you want to ask the question like, why, me? Right?
1:47:36
Ronghui Gu: Right, for example. Certainly. Why? Me? Because well, I'm a professor working on as a cyber security, right? I've also papers about this penalty, something like that. Right? This is
1:47:40
Ronghui Gu: how I explain why, me? Right? Like. When you explain why why you you can.
1:47:50
Ronghui Gu: you can may not be. You may not have the the this technology. And so but you need to find a way to demonstrate why you might as well, you have tried something, or you have accumulate. Let's say the the basis and the need for this, or you have been dreaming of it for your time be preparing for for many years. So 1st thing you need to answer by me, actually, not one.
1:47:56
Ronghui Gu: You actually. It's why you're a team something like that right? Then you want to show what you gotta do
1:48:21
Ronghui Gu: right? Working on, too. And this is
1:48:27
Ronghui Gu: even for 0, you wanna say eventually, what do you wanna do
1:48:30
Ronghui Gu: right. You want to create the ultimate
1:48:35
Ronghui Gu: form of your product, your comp company, and what kind of how large this market, how large the market address
1:48:38
Ronghui Gu: right? And to give people a sense that if you succeed, if you can reach that ultimate goal right? How much your company works right? What's the value you create for this society? Right? You need to have that even for c 1. And then you need some milestone to reach there
1:48:46
Ronghui Gu: the 1st milestone. You have to make it a little bit more concrete and implementable, right? The next one as well
1:49:03
Ronghui Gu: as long as you can. You can have some of them which you are ultimate goal. It's okay. Therefore, first, st you wasn't.
1:49:12
Ronghui Gu: What what do you need to track? It does actually, if you successfully with the
1:49:20
Ronghui Gu: the thought, right?
1:49:27
Ronghui Gu: How you want to spend money.
1:49:28
Ronghui Gu: And what do you wanna do with this money like you wanna do?
1:49:30
Ronghui Gu: The protocol is for us
1:49:35
Ronghui Gu: to attract, let's say
1:49:36
Ronghui Gu: 100,000 users right? Or you have
1:49:40
Ronghui Gu: 100 or 10 or 10 enterprise clients right by work days.
1:49:44
Ronghui Gu: Right? And they say, well, we have a team of 10 right myself as co-founder. I will not receive any salary but the other 8 right now they need salary, and I calculate, and we need one year to build this. So that's why we need this amount of money. And then we need a little bit more space. And by one year 10 of us can do this. And then after that stage, we're gonna do another round of fundraiser, something like that right to reach the next stage. So that's what we want to cover
1:49:52
Ronghui Gu: progressive online. Yeah, yeah.
1:50:21
Ronghui Gu: what? What do you want to do to spend this money? And the next stage. Right? What do you want to achieve after we successfully right after you burn out all the money is. Now, what do you want to do? Right? You need that 2 stages.
1:50:24
Ronghui Gu: add a
1:50:37
Ronghui Gu: yeah, that's basically what it will need for this seed. Raw business plan
1:50:38
Ronghui Gu: right? And then, once we have this.
1:50:45
Ronghui Gu: what do you? What you need is practice right? You can get your friends right. Some family members present your idea, pitch yourself to them to see if they have interest. So this should be kind of 15 min to see if you can attract them
1:50:47
Ronghui Gu: right? And then you can go to some incubator programs apply for right? You can basically go to other. It's not that hard to to search this early basis
1:51:03
Ronghui Gu: the good thing is, if you can't have any connection
1:51:18
Ronghui Gu: with other people from them. That way will be much better than a cold email.
1:51:22
Ronghui Gu: So, Julie, a cold email
1:51:26
Ronghui Gu: does not work
1:51:29
Ronghui Gu: because most of the investors. You can imagine how many emails you will receive. You can imagine how many emails I will receive as a professor. Right? So kind of like many emails.
1:51:31
Ronghui Gu: will be simply ignored. Push into
1:51:40
Ronghui Gu: Job
1:51:44
Ronghui Gu: a trash-trash kind of like the trash box, something like that. So Co email related now or so, what you want to do is you want to?
1:51:46
Ronghui Gu: You want it somewhat
1:51:55
Ronghui Gu: right? Who works in this business? Actually, you is not that very hard? Why.
1:51:57
Ronghui Gu: you're nice. You're calling your students right? You just go online, check this early stages. Try to be there. These partners, right? Or manage- managing directors
1:52:04
Ronghui Gu: right? Check their their background. You definitely find someone graduate from Columbia right? Right? And then you can reach out to them through Columbia resources. Right?
1:52:14
Ronghui Gu: Really, it's not that hard, and you don't need to reach out to someone with a big name.
1:52:26
Ronghui Gu: a partner. Actually, that's that's even not a good good idea. Because really, these big partners.
1:52:32
Ronghui Gu: They do not review
1:52:39
Ronghui Gu: projects by themselves.
1:52:41
Ronghui Gu: They have some, let's say, early. They have some investors or managing directors or Vps reporting to them who will be reviewing projects. So even if you reach out to this partner as well.
1:52:43
Ronghui Gu: the most they will do is forward your email to someone working for him. So
1:52:55
Ronghui Gu: somehow, even if you know or you, you can get connected with someone. Let's say.
1:53:00
Ronghui Gu: pretty truly important that this is. Actually, it's it's good.
1:53:06
Ronghui Gu: Yeah, yours is.
1:53:09
Ronghui Gu: It's not that hard to to count.
1:53:12
Ronghui Gu: to, to connect, to become network. Yeah. So try to get in touch with someone that you can find right
1:53:14
Ronghui Gu: and and present it to them, receive feedbacks and keep doing and keep going good.
1:53:23
Ronghui Gu: Go ahead. Issue any programs like one company.
1:53:30
Ronghui Gu: Oh, why, Commander.
1:53:32
Ronghui Gu: any programs like that like incubating programs. You mean any other incubation programs that why come in or want me to explain why commitment.
1:53:34
Ronghui Gu: did you, you know, join any of these programs. Oh, no, we didn't join any kind of innovation programs. So for students, I may recommend you to join these incubation programs. But for for now, because, you know, when we started, we already have lots of you know, technologies, patterns, and so on. We don't need to start from that 1st
1:53:44
Ronghui Gu: any other questions we'll see. What's
1:54:06
Ronghui Gu: do. We need a public cluster usage here.
1:54:09
Ronghui Gu: I mean the
1:54:12
Ronghui Gu: this professorship. Whether this is
1:54:14
Ronghui Gu: I'm sorry. Oh, Colombia at Chile, at Colombia. That's a good question. So 1st of all, I would say, Columbia has lots of
1:54:18
Ronghui Gu: startup resources.
1:54:26
Ronghui Gu: So that's good thing. For example, Colombia, I love even have this own
1:54:28
Ronghui Gu: incubation program
1:54:33
Ronghui Gu: bye. Absolutely. So.
1:54:34
Ronghui Gu: Columbia has its own innovation program. And I know some peer students here. They get a some small tax from them, $100,000, or $200,000 from them to service. And that. That's 1 good thing. Second, I would say, Columbia.
1:54:35
Ronghui Gu: There are
1:54:52
Ronghui Gu: many, many professors, especially as Cis Department right. Many professors have their startups or have their companies. So it means us well.
1:54:53
Ronghui Gu: You can easily connect with them. Right? Get some resources and get some help. And for me particularly, I would say definitely, help
1:55:02
Ronghui Gu: help a lot actually and support me very, very much. And also, people definitely recognize this. Professorship. Recognize your technical strength right as well. But in the
1:55:10
Ronghui Gu: at some stage
1:55:24
Ronghui Gu: it may not be that helpful or even hurt a little bit. That is
1:55:26
Ronghui Gu: well, I'll put it this way. Most of Vcs do not want to invest professors company.
1:55:31
Ronghui Gu: Why? Because,
1:55:38
Ronghui Gu: the chance to succeed is very, very small
1:55:40
Ronghui Gu: for professors. Reason, there are many model reasons. One reason is, well, you feel like well, this your audience, professor? Right? So you're not that motivated
1:55:44
Ronghui Gu: right to build this company right? So this is 1st reason. Second reason is that
1:55:54
Ronghui Gu: well, Professor.
1:55:59
Ronghui Gu: kind of like when you run a research lab as a professor is pretty much like running a pre a stage company.
1:56:02
Ronghui Gu: Oh, okay, yeah, okay, yeah. So, but so mean, that's professor is pretty good at running a companies from Earth's starting day to
1:56:11
Ronghui Gu: to to service a. But after that well, let's has no advantages.
1:56:22
Ronghui Gu: Okay, we'll stop it.
1:56:29
Auto-play is disabled in your web browser. Press play to start.

"""
    base_url = data.get('base_url')

    print(base_url)

    if not transcript or not base_url:
        return jsonify({"error": "Missing transcript or base_url"}), 400

    try:
        notes = generate_class_notes(transcript)
        html_content = create_html_content(notes, base_url)
        return jsonify({"html_content": html_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)