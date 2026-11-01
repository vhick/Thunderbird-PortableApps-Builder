// Original launcher source for Thunderbird Community Portable. MIT license; see LICENSE-LAUNCHER.txt.
// No elevation, shell integration, injection, registry changes, or code packing.
#define UNICODE
#define _UNICODE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <algorithm>
#include <cwctype>
#include <filesystem>
#include <fstream>
#include <string>
#include <stdexcept>
#include <vector>
namespace fs = std::filesystem;

static void error(const std::wstring& msg) { MessageBoxW(nullptr,msg.c_str(),L"Thunderbird Community Portable",MB_OK|MB_ICONERROR); }
static std::wstring quote(const std::wstring& s) {
    std::wstring o=L"\""; unsigned slash=0;
    for(wchar_t c:s) {
        if(c==L'\\'){++slash;continue;}
        if(c==L'"') {o.append(slash*2+1,L'\\');o+=L'"';slash=0;continue;}
        o.append(slash,L'\\');slash=0;o+=c;
    }
    o.append(slash*2,L'\\');o+=L'"';return o;
}
static std::wstring lower(std::wstring s) { std::transform(s.begin(),s.end(),s.begin(),[](wchar_t c){return std::towlower(c);});return s; }
static std::string utf8(const std::wstring& w) {
    int n=WideCharToMultiByte(CP_UTF8,0,w.c_str(),(int)w.size(),nullptr,0,nullptr,nullptr);
    std::string o(n,'\0');if(n)WideCharToMultiByte(CP_UTF8,0,w.c_str(),(int)w.size(),o.data(),n,nullptr,nullptr);return o;
}
static std::wstring unutf8(const std::string& s) {
    int n=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,s.data(),(int)s.size(),nullptr,0);
    std::wstring o(n,L'\0');if(n)MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,s.data(),(int)s.size(),o.data(),n);return o;
}
static std::string slashesForJS(const std::wstring& s) {
    std::string src=utf8(s), o;
    for(char c:src) {if(c=='\\')o+="\\\\";else if(c=='"')o+="\\\"";else o+=c;}
    return o;
}
static std::string readAll(const fs::path& p) {std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
static void writeAll(const fs::path& p,const std::string& s) {
    std::ofstream f(p,std::ios::binary|std::ios::trunc);if(!f)throw std::runtime_error("Cannot write file");
    f.write(s.data(),(std::streamsize)s.size());if(!f)throw std::runtime_error("Incomplete file write");
}
// Only rewrite Thunderbird-owned, known absolute profile/mail-store prefs when the whole app moves.
// External mail-store paths are intentionally NOT replaced. Keep a pristine backup.
static void migrate(const fs::path& data,const fs::path& profile) {
    auto record=data/L"settings"/L"last-location.txt";
    fs::create_directories(record.parent_path());
    std::wstring current=fs::absolute(data.parent_path()).lexically_normal().wstring();
    std::wstring previous;
    if(fs::exists(record))previous=unutf8(readAll(record));
    if(!previous.empty() && lower(previous)!=lower(current)) {
        auto pref=profile/L"prefs.js";
        if(fs::exists(pref)) {
            std::string oldJs=slashesForJS(previous), newJs=slashesForJS(current);
            std::string oldForward=utf8(previous), newForward=utf8(current);
            std::replace(oldForward.begin(),oldForward.end(),'\\','/');
            std::replace(newForward.begin(),newForward.end(),'\\','/');
            std::string original=readAll(pref), updated, line;
            size_t cursor=0;
            while(cursor<original.size()) {
                size_t end=original.find('\n',cursor);
                if(end==std::string::npos)end=original.size();
                line=original.substr(cursor,end-cursor);
                // Target only well-known Thunderbird mail paths, not arbitrary external references.
                bool mailPref=(line.rfind("user_pref(\"mail.root.",0)==0 ||
                    (line.rfind("user_pref(\"mail.server.server",0)==0 && line.find(".directory\"")!=std::string::npos));
                if(mailPref) {
                    auto replacePrefix=[&](const std::string& from,const std::string& to){
                        size_t pos=line.find(from);
                        while(pos!=std::string::npos) {
                            // Match old portable ROOT followed by separator; no unrelated paths.
                            size_t after=pos+from.size();
                            if(after<line.size() && (line[after]=='\\'||line[after]=='/')) {
                                line.replace(pos,from.size(),to);pos=line.find(from,pos+to.size());
                            } else pos=line.find(from,after);
                        }
                    };
                    replacePrefix(oldJs,newJs);replacePrefix(oldForward,newForward);
                }
                updated+=line;
                if(end<original.size())updated+='\n';
                cursor=end+1;
            }
            if(updated!=original) {
                auto backup=pref;backup+=L".before-portable-relocation.bak";
                fs::copy_file(pref,backup,fs::copy_options::overwrite_existing);
                auto temp=pref;temp+=L".portable.tmp";
                writeAll(temp,updated);
                if(!MoveFileExW(temp.c_str(),pref.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))
                    throw std::runtime_error("Could not atomically update Thunderbird prefs.js after relocation");
            }
        }
    }
    writeAll(record,utf8(current));
}
int WINAPI wWinMain(HINSTANCE,HINSTANCE,LPWSTR,int) {
    try {
        wchar_t module[32768];DWORD n=GetModuleFileNameW(nullptr,module,32768);
        if(!n||n>=32768) {error(L"Cannot find launcher path.");return 1;}
        fs::path root=fs::path(module).parent_path();
        fs::path tb=root/L"App"/L"Thunderbird"/L"thunderbird.exe";
        fs::path data=root/L"Data";
        fs::path profile=data/L"profile";
        fs::path tmp=data/L"temp";
        if(!fs::is_regular_file(tb)) {error(L"Thunderbird program not found: "+tb.wstring());return 2;}
        fs::create_directories(profile);fs::create_directories(tmp);
        // One launcher per portable directory. No effect on installed Thunderbird instances.
        std::wstring canonical=lower(fs::absolute(root).lexically_normal().wstring());
        unsigned long long h=14695981039346656037ull;
        for(auto c:canonical){h^=(unsigned long long)c;h*=1099511628211ull;}
        std::wstring mutexName=L"Local\\ThunderbirdCommunityPortable_"+std::to_wstring(h);
        HANDLE mutex=CreateMutexW(nullptr,FALSE,mutexName.c_str());
        if(!mutex) {error(L"Cannot create the portable instance lock.");return 3;}
        if(GetLastError()==ERROR_ALREADY_EXISTS) {error(L"This portable Thunderbird is already running. Close it before relaunching or updating.");CloseHandle(mutex);return 4;}
        migrate(data,profile);
        int argc=0;LPWSTR* argv=CommandLineToArgvW(GetCommandLineW(),&argc);
        std::wstring args;
        bool diagnostics=false;
        if(argc==2 && argv && std::wstring(argv[1])==L"--portable-diagnostics")diagnostics=true;
        for(int i=1;i<argc && !diagnostics;++i) {
            std::wstring arg=lower(argv[i]);
            if(arg==L"-p"||arg==L"--profile"||arg==L"-profile"||arg==L"-profilemanager"||arg==L"--profilemanager"||arg==L"-no-remote"||arg==L"--no-remote") {
                error(L"Profile override arguments are blocked to protect the portable profile.");if(argv)LocalFree(argv);CloseHandle(mutex);return 5;
            }
            args+=L" "+quote(argv[i]);
        }
        if(argv)LocalFree(argv);
        if(diagnostics) {CloseHandle(mutex);return (fs::exists(profile)&&fs::exists(tb))?0:6;}
        SetEnvironmentVariableW(L"TEMP",tmp.c_str());SetEnvironmentVariableW(L"TMP",tmp.c_str());
        // Portable profile is selected BEFORE launching Thunderbird. No host profile is imported.
        std::wstring command=quote(tb.wstring())+L" -no-remote -profile "+quote(profile.wstring())+args;
        std::vector<wchar_t> cmd(command.begin(),command.end());cmd.push_back(L'\0');
        STARTUPINFOW si{};si.cb=sizeof(si);PROCESS_INFORMATION pi{};
        std::wstring cwd=tb.parent_path().wstring();
        if(!CreateProcessW(tb.c_str(),cmd.data(),nullptr,nullptr,FALSE,0,nullptr,cwd.c_str(),&si,&pi)) {
            DWORD code=GetLastError();error(L"Could not start Thunderbird (Windows error "+std::to_wstring(code)+L").");CloseHandle(mutex);return 7;
        }
        CloseHandle(pi.hThread);
        WaitForSingleObject(pi.hProcess,INFINITE);
        DWORD code=1;GetExitCodeProcess(pi.hProcess,&code);CloseHandle(pi.hProcess);CloseHandle(mutex);
        return (int)code;
    } catch(const std::exception& e) {error(L"Portable data error. Check the Data directory is writable.\n"+unutf8(e.what()));return 10;}
}
