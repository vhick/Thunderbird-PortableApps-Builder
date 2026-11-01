// Thunderbird Portable TraceGuard r7 — MIT license, see LICENSE-LAUNCHER.txt.
// Conservative pre/post-session directory ownership checks. No administrator rights,
// registry modification, process termination, or removal of existing user data.
#pragma once
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <array>
#include <algorithm>
#include <cstdint>
#include <cwchar>
#include <string>
#include <vector>
#include <system_error>
#include <stdexcept>

namespace traceguard {
namespace fs = std::filesystem;
struct Roots {
    fs::path roaming;
    fs::path local;
    fs::path programData;
    fs::path localLow; // Stormhen tracks USERPROFILE\AppData\LocalLow\Thunderbird.
};
inline fs::path environment_path(const wchar_t* key) {
    DWORD required=GetEnvironmentVariableW(key,nullptr,0);
    if(required==0 || required>32768)return {};
    std::wstring buffer(required,L'\0');
    DWORD actual=GetEnvironmentVariableW(key,buffer.data(),required);
    if(!actual || actual>=required)return {};
    buffer.resize(actual);
    return fs::path(buffer);
}
inline Roots windows_roots() {
    const fs::path user=environment_path(L"USERPROFILE");
    const fs::path low=user.empty()?fs::path{}:user/L"AppData"/L"LocalLow";
    return {environment_path(L"APPDATA"),environment_path(L"LOCALAPPDATA"),
            environment_path(L"ProgramData"),low};
}
inline bool is_reparse(const fs::path& p) {
    DWORD a=GetFileAttributesW(p.c_str());
    return a!=INVALID_FILE_ATTRIBUTES && (a & FILE_ATTRIBUTE_REPARSE_POINT)!=0;
}
inline bool trace_exists(const fs::path& p) {
    std::error_code ec;
    return !p.empty() && fs::exists(p,ec) && !ec;
}
inline bool trace_is_directory(const fs::path& p) {
    std::error_code ec;
    return fs::is_directory(p,ec) && !ec;
}
inline bool is_empty_directory(const fs::path& p) {
    std::error_code ec;
    return trace_is_directory(p) && fs::is_empty(p,ec) && !ec;
}
inline std::string utf8(const std::wstring& src) {
    int needed=WideCharToMultiByte(CP_UTF8,0,src.c_str(),(int)src.size(),nullptr,0,nullptr,nullptr);
    if(needed<=0)return "";
    std::string s(needed,'\0');
    WideCharToMultiByte(CP_UTF8,0,src.c_str(),(int)src.size(),s.data(),needed,nullptr,nullptr);
    return s;
}
inline std::string path_text(const fs::path& p) {return utf8(p.wstring());}
inline std::wstring session_id() {
    SYSTEMTIME st{};GetSystemTime(&st);
    wchar_t time[90];
    swprintf_s(time,_countof(time),L"%04u%02u%02u-%02u%02u%02u-%lu-%llu",st.wYear,st.wMonth,st.wDay,
        st.wHour,st.wMinute,st.wSecond,GetCurrentProcessId(),
        static_cast<unsigned long long>(GetTickCount64()));
    return time;
}
// A cross-volume move of a *directory* is not supported by MoveFileExW.
// Copy to the portable destination, check every byte and directory entry,
// then remove the source only if the verified copy is complete and exclusive.
// Refuse reparse points and unexpectedly large trees; keep the source on failure.
inline bool equal_file_contents(const fs::path& a,const fs::path& b) {
    std::ifstream ia(a,std::ios::binary),ib(b,std::ios::binary);
    if(!ia || !ib)return false;
    std::array<char,65536> ba{},bb{};
    for(;;) {
        ia.read(ba.data(),ba.size());ib.read(bb.data(),bb.size());
        auto na=ia.gcount(),nb=ib.gcount();
        if(na!=nb || !std::equal(ba.begin(),ba.begin()+na,bb.begin()))return false;
        if(na==0)return true;
    }
}
inline bool verify_tree(const fs::path& source,const fs::path& dest) {
    std::error_code ec;
    if(is_reparse(source) || is_reparse(dest))return false;
    std::uintmax_t bytes=0;
    size_t count=0;
    for(fs::recursive_directory_iterator it(source,fs::directory_options::none,ec),end;
        !ec && it!=end;it.increment(ec)) {
        if(++count>20000 || is_reparse(it->path()))return false;
        fs::path rel=it->path().lexically_relative(source);
        fs::path target=dest/rel;
        if(it->is_directory(ec)) {
            if(!trace_is_directory(target) || is_reparse(target))return false;
        } else if(it->is_regular_file(ec)) {
            auto size=it->file_size(ec);
            if(ec || size>512ull*1024*1024 || bytes>512ull*1024*1024-size)return false;
            bytes+=size;
            if(!fs::is_regular_file(target,ec) || ec || fs::file_size(target,ec)!=size || ec)return false;
            if(!equal_file_contents(it->path(),target))return false;
        } else return false;
        if(ec)return false;
    }
    if(ec)return false;
    // Include both directions so a changed or unexpected destination is rejected.
    size_t destCount=0;
    for(fs::recursive_directory_iterator it(dest,fs::directory_options::none,ec),end;
        !ec && it!=end;it.increment(ec)){
        if(++destCount>count || is_reparse(it->path()))return false;
    }
    return !ec && destCount==count;
}
// Check the entire source tree before ANY move/copy. Limit work and reject
// reparse points, junctions, device entries and unexpectedly large captures.
inline bool safe_source_tree(const fs::path& source) {
    if(!trace_is_directory(source) || is_reparse(source))return false;
    std::error_code ec;
    size_t count=0;
    std::uintmax_t bytes=0;
    for(fs::recursive_directory_iterator it(source,fs::directory_options::none,ec),end;
        !ec && it!=end;it.increment(ec)) {
        if(++count>20000 || is_reparse(it->path()))return false;
        if(it->is_regular_file(ec)) {
            auto length=it->file_size(ec);
            if(ec || length>512ull*1024*1024 || bytes>512ull*1024*1024-length)return false;
            bytes+=length;
        } else if(!it->is_directory(ec))return false;
        if(ec)return false;
    }
    return !ec;
}
inline bool capture_directory(const fs::path& source,const fs::path& dest) {
    if(trace_exists(dest) || !safe_source_tree(source) || is_reparse(dest.parent_path()))return false;
    if(MoveFileExW(source.c_str(),dest.c_str(),MOVEFILE_WRITE_THROUGH))return true;
    // Cross-volume fallback. Do NOT try if the initial failure was unrelated.
    if(GetLastError()!=ERROR_NOT_SAME_DEVICE)return false;
    const fs::path pending=dest.wstring()+L".pending";
    if(trace_exists(pending))return false;
    std::error_code ec;
    fs::copy(source,pending,fs::copy_options::recursive,ec);
    if(ec || !verify_tree(source,pending))return false;
    fs::rename(pending,dest,ec);
    if(ec || !verify_tree(source,dest))return false;
    // Source was exclusively absent before this portable session and must still
    // match the captured bytes. A failed removal leaves the copy for recovery.
    if(!verify_tree(source,dest))return false;
    fs::remove_all(source,ec);
    return !ec && !trace_exists(source);
}
struct Watch {
    fs::path path;
    fs::path relativeCapture;
    bool dedicated=false;
    bool removeIfEmpty=false;
    bool wasPresent=false;
    bool wasReparse=false;
};
class Session {
    fs::path base_;
    std::wstring id_;
    std::vector<Watch> watches_;
    fs::path logFile_;
    bool valid_=false;
    void note(const std::string& line) const {
        // Failure to write the audit log cannot be used to justify destructive cleanup.
        std::ofstream log(logFile_,std::ios::binary|std::ios::app);
        if(log)log<<line<<"\n";
    }
    void add(fs::path p,fs::path capture,bool dedicated,bool removeIfEmpty=false) {
        if(p.empty())return;
        Watch w{};w.path=std::move(p);w.relativeCapture=std::move(capture);
        w.dedicated=dedicated;w.removeIfEmpty=removeIfEmpty;w.wasPresent=trace_exists(w.path);w.wasReparse=is_reparse(w.path);
        watches_.push_back(std::move(w));
    }
public:
    // Explicit roots permit a standalone offline Windows fixture test with no real host changes.
    Session(fs::path portableData,Roots roots): base_(std::move(portableData)),id_(session_id()) {
        try {
            fs::create_directories(base_/L"TraceGuard"/L"logs");
            logFile_=base_/L"TraceGuard"/L"logs"/(L"session-"+id_+L".txt");
            {std::ofstream check(logFile_,std::ios::binary|std::ios::app);
             if(!check)throw std::runtime_error("TraceGuard log path is not writable");}
            note("TRACEGUARD r7 start: only newly CREATED dedicated Thunderbird roots can be relocated.");
            note("Existing folders and shared Mozilla/ProgramData/gnupg trees are PROTECTED.");
            if(!roots.roaming.empty()) {
                add(roots.roaming/L"Thunderbird",fs::path(L"Roaming")/L"Thunderbird",true);
                add(roots.roaming/L"Mozilla",{},false,true);
            }
            if(!roots.local.empty()) {
                add(roots.local/L"Thunderbird",fs::path(L"Local")/L"Thunderbird",true);
                add(roots.local/L"Mozilla",{},false,true);
                add(roots.local/L"gnupg",{},false); // GnuPG key material: NEVER modify.
            }
            // Stormhen also monitors LocalLow. Capture only if absent at session start.
            if(!roots.localLow.empty()) {
                add(roots.localLow/L"Thunderbird",fs::path(L"LocalLow")/L"Thunderbird",true);
            }
            if(!roots.programData.empty()) {
                add(roots.programData/L"Mozilla",{},false);
                add(roots.programData/L"Mozilla-1de4eec8-1241-4177-a864-e594e8d1fb38",{},false);
                add(roots.programData/L"Thunderbird",{},false);
            }
            for(const auto& w:watches_) {
                note("BEFORE | "+path_text(w.path)+" | "+
                    (w.wasPresent?"PRESENT -- never move":"ABSENT")+
                    (w.dedicated?" | dedicated":" | shared/report only")+
                    (w.wasReparse?" | reparse point":""));
            }
            valid_=true;
        } catch(const std::exception&) {valid_=false;}
    }
    bool ready() const {return valid_;}
    const fs::path& log_path() const {return logFile_;}
    void finish(bool cleanShutdown, bool otherThunderbirdProcessRunning) {
        if(!valid_)return;
        const bool mayMove=cleanShutdown && !otherThunderbirdProcessRunning;
        note(std::string("AFTER | cleanShutdown=")+(cleanShutdown?"yes":"no")+
             " | otherThunderbirdProcessRunning="+(otherThunderbirdProcessRunning?"yes":"no"));
        for(const auto& w:watches_) {
            if(w.wasPresent) { note("KEEP pre-existing | "+path_text(w.path));continue; }
            if(!trace_exists(w.path)) { note("NO TRACE | "+path_text(w.path));continue; }
            // Never traverse a junction/symlink or delete inside an unknown reparse tree.
            if(w.wasReparse || is_reparse(w.path) || is_reparse(w.path.parent_path()) || !trace_is_directory(w.path)) {
                note("KEEP suspicious type/reparse point | "+path_text(w.path));continue;
            }
            if(!mayMove) {note("KEEP uncertain shutdown/process ownership | "+path_text(w.path));continue;}
            if(!w.dedicated) {
                // Remove ONLY an entire empty, newly-created Mozilla parent.
                // ProgramData and gnupg are ALWAYS audit-only even when empty.
                if(w.removeIfEmpty && is_empty_directory(w.path)) {
                    std::error_code ec;
                    const bool removed=fs::remove(w.path,ec);
                    note(std::string(removed && !ec?"REMOVED newly created EMPTY shared parent | ":"KEEP shared parent | ")+path_text(w.path));
                } else note("KEEP shared application directory | "+path_text(w.path));
                continue;
            }
            // Never discard data. Move exactly the previously absent, dedicated top-level
            // Thunderbird directory into an entirely new, session-named destination.
            fs::path destination=base_/L"TraceGuard"/L"captured"/w.relativeCapture/(L"session-"+id_);
            try {
                if(trace_exists(destination) || is_reparse(destination.parent_path())) {
                    note("KEEP destination exists or is a junction | "+path_text(w.path));continue;
                }
                fs::create_directories(destination.parent_path());
                // Same-drive directory rename is atomic. For a different volume,
                // copy, verify every file and then remove only the dedicated source.
                if(!capture_directory(w.path,destination)) {
                    note("KEEP capture failed or was unsafe; original retained if possible | "+path_text(w.path));
                } else {
                    note("CAPTURED | "+path_text(w.path)+" -> "+path_text(destination));
                }
            } catch(const std::exception&) {
                note("KEEP exception while preparing safe capture path | "+path_text(w.path));
            }
        }
        note("TRACEGUARD r7 complete. Pre-existing host folders are untouched.");
    }
};
} // namespace traceguard
